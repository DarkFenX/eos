#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2013 Anton Vorobyov
#
# This file is part of Eos.
#
# Eos is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eos is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Eos. If not, see <http://www.gnu.org/licenses/>.
#===============================================================================


from eos.const.eve import Attribute
from eos.util.frozen_dict import FrozenDict
from .modifier_builder import ModifierBuilder


class Converter:
    """
    Class responsible for transforming data structure,
    like moving data around or converting whole data
    structure.
    """

    def __init__(self, logger):
        self._logger = logger

    def normalize(self, data):
        """ Make data more consistent."""
        self.data = data
        self._move_attribs()

    def _move_attribs(self):
        """
        Some of item attributes are defined in invtypes table.
        We do not need them there, for data consistency it's worth
        to move them to dgmtypeattribs table.
        """
        atrrib_map = {'radius': Attribute.radius,
                      'mass': Attribute.mass,
                      'volume': Attribute.volume,
                      'capacity': Attribute.capacity}
        attr_ids = tuple(atrrib_map.values())
        # Here we will store pairs (typeID, attrID) already
        # defined in table
        defined_pairs = set()
        dgmtypeattribs = self.data['dgmtypeattribs']
        for row in dgmtypeattribs:
            if row['attributeID'] not in attr_ids:
                continue
            defined_pairs.add((row['typeID'], row['attributeID']))
        attrs_skipped = 0
        new_invtypes = set()
        # Cycle through all invtypes, for each row moving each its field
        # either to different table or container for updated rows
        for row in self.data['invtypes']:
            type_id = row['typeID']
            new_row = {}
            for field, value in row.items():
                if field in atrrib_map:
                    # If row didn't have such attribute defined, skip it
                    if value is None:
                        continue
                    # If such attribute already exists in dgmtypeattribs,
                    # do not modify it - values from dgmtypeattribs table
                    # have priority
                    attr_id = atrrib_map[field]
                    if (type_id, attr_id) in defined_pairs:
                        attrs_skipped += 1
                        continue
                    # Generate row and add it to proper attribute table
                    dgmtypeattribs.add(FrozenDict({'typeID': type_id,
                                                   'attributeID': attr_id,
                                                   'value': value}))
                else:
                    new_row[field] = value
            new_invtypes.add(FrozenDict(new_row))
        # Update invtypes with rows which do not contain attributes
        self.data['invtypes'].clear()
        self.data['invtypes'].update(new_invtypes)
        if attrs_skipped > 0:
            msg = '{} built-in attributes already have had value in dgmtypeattribs and were skipped'.format(
                attrs_skipped)
            self._logger.warning(msg, child_name='cache_generator')

    def convert(self, data):
        """
        Convert database-like data structure to eos-
        specific one.
        """
        data = self._assemble(data)
        self._build_modifiers(data)
        return data

    def _assemble(self, data):
        """
        Use passed data to compose object-like data rows,
        as in, to 'assemble' objects.
        """
        # Before actually generating rows, we need to collect
        # some data in convenient form
        # Format: {type ID: type row}
        dgmeffects_keyed = {}
        for row in data['dgmeffects']:
            dgmeffects_keyed[row['effectID']] = row
        # Format: {group ID: group row}
        invgroups_keyed = {}
        for row in data['invgroups']:
            invgroups_keyed[row['groupID']] = row
        # Format: {type ID: default effect ID}
        type_defeff_map = {}
        for row in data['dgmtypeeffects']:
            if row.get('isDefault') is True:
                type_defeff_map[row['typeID']] = row['effectID']
        # Format: {type ID: [effect IDs]}
        type_effects = {}
        for row in data['dgmtypeeffects']:
            type_effects_row = type_effects.setdefault(row['typeID'], [])
            type_effects_row.append(row['effectID'])
        # Format: {type ID: {attr ID: value}}
        type_attribs = {}
        for row in data['dgmtypeattribs']:
            type_attribs_row = type_attribs.setdefault(row['typeID'], {})
            type_attribs_row[row['attributeID']] = row['value']

        # We will build new data structure from scratch
        assembly = {}

        types = []
        for row in data['invtypes']:
            type_id = row['typeID']
            group_id = row.get('groupID')
            # Get effect row of default effect, replacing it
            # with empty dictionary if there's no one
            if type_id in type_defeff_map:
                defeff = dgmeffects_keyed.get(type_defeff_map[type_id], {})
            else:
                defeff = {}
            type_ = {
                'type_id': type_id,
                'group_id': group_id,
                'category_id': invgroups_keyed.get(group_id, {}).get('categoryID'),
                'duration_attribute_id': defeff.get('durationAttributeID'),
                'discharge_attribute_id': defeff.get('dischargeAttributeID'),
                'range_attribute_id': defeff.get('rangeAttributeID'),
                'falloff_attribute_id': defeff.get('falloffAttributeID'),
                'tracking_speed_attribute_id': defeff.get('trackingSpeedAttributeID'),
                'effects': type_effects.get(type_id, []),
                'attributes': type_attribs.get(type_id, {})
            }
            types.append(type_)
        assembly['types'] = types

        attributes = []
        for row in data['dgmattribs']:
            attribute = {
                'attribute_id': row['attributeID'],
                'max_attribute_id': row.get('maxAttributeID'),
                'default_value': row.get('defaultValue'),
                'high_is_good': row.get('highIsGood'),
                'stackable': row.get('stackable')
            }
            attributes.append(attribute)
        assembly['attributes'] = attributes

        effects = []
        assembly['effects'] = []
        for row in data['dgmeffects']:
            effect = {
                'effect_id': row['effectID'],
                'effect_category': row.get('effectCategory'),
                'is_offensive': row.get('isOffensive'),
                'is_assistance': row.get('isAssistance'),
                'fitting_usage_chance_attribute_id': row.get('fittingUsageChanceAttributeID'),
                'pre_expression_id': row.get('preExpression'),
                'post_expression_id': row.get('postExpression')
            }
            effects.append(effect)
        assembly['effects'] = effects

        assembly['expressions'] = list(data['dgmexpressions'])

        return assembly

    def _build_modifiers(self, data):
        """
        Replace expressions with generated out of
        them modifiers.
        """
        builder = ModifierBuilder(data['expressions'], self._logger)
        # Lists effects, which are using given modifier
        # Format: {modifier row: [effect IDs]}
        modifier_effect_map = {}
        # Prepare to give each modifier unique ID
        # Format: {modifier row: modifier ID}
        modifier_id_map = {}
        modifier_id = 1
        # Sort rows by ID so we numerate modifiers in deterministic way
        for effect_row in sorted(data['effects'], key=lambda row: row['effect_id']):
            modifiers, build_status = builder.build_effect(effect_row['pre_expression_id'],
                                                           effect_row['post_expression_id'],
                                                           effect_row['effect_category'])
            # Update effects: add modifier build status and remove
            # fields which we needed only for this process
            effect_row['build_status'] = build_status
            del effect_row['pre_expression_id']
            del effect_row['post_expression_id']
            for modifier in modifiers:
                # Convert modifiers into frozen datarows to use
                # them in conversion process
                frozen_modifier = self._freeze_modifier(modifier)
                # Gather data about which effects use which modifier
                used_by_effects = modifier_effect_map.setdefault(frozen_modifier, [])
                used_by_effects.append(effect_row['effect_id'])
                # Assign ID only to each unique modifier
                if frozen_modifier not in modifier_id_map:
                    modifier_id_map[frozen_modifier] = modifier_id
                    modifier_id += 1

        # Compose reverse to modifier_effect_map dictionary
        # Format: {effect ID: [modifier rows]}
        effect_modifier_map = {}
        for frozen_modifier, effect_ids in modifier_effect_map.items():
            for effect_id in effect_ids:
                effect_modifiers = effect_modifier_map.setdefault(effect_id, [])
                effect_modifiers.append(frozen_modifier)

        # For each effect, add IDs of each modifiers it uses
        for effect_row in data['effects']:
            modifier_ids = []
            for frozen_modifier in effect_modifier_map.get(effect_row['effect_id'], ()):
                modifier_ids.append(modifier_id_map[frozen_modifier])
            effect_row['modifiers'] = modifier_ids

        # Replace expressions table with modifiers
        del data['expressions']
        modifiers = []
        for frozen_modifier, modifier_id in modifier_id_map.items():
            modifier = {}
            modifier.update(frozen_modifier)
            modifier['modifier_id'] = modifier_id
            modifiers.append(modifier)
        data['modifiers'] = modifiers

    def _freeze_modifier(self, modifier):
        """
        Converts modifier into frozendict with its keys and
        values assigned according to modifier's ones.
        """
        # Fields which we need to dump into row
        fields = ('state', 'context', 'source_attribute_id', 'operator',
                  'target_attribute_id', 'location', 'filter_type', 'filter_value')
        modifier_row = {}
        for field in fields:
            modifier_row[field] = getattr(modifier, field)
        frozen_row = FrozenDict(modifier_row)
        return frozen_row