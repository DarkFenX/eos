# ===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2017 Anton Vorobyov
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
# ===============================================================================


from eos import *
from eos.const.eve import Attribute, Effect, EffectCategory
from tests.integration.item.item_testcase import ItemMixinTestCase


class TestItemDamageDoomsday(ItemMixinTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.em_damage)
        self.ch.attribute(attribute_id=Attribute.thermal_damage)
        self.ch.attribute(attribute_id=Attribute.kinetic_damage)
        self.ch.attribute(attribute_id=Attribute.explosive_damage)
        self.cycle_attr = self.ch.attribute()
        self.effect = self.ch.effect(
            effect_id=Effect.super_weapon_amarr, category=EffectCategory.active, duration_attribute=self.cycle_attr.id
        )

    def test_nominal_volley_generic(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.em_damage: 52000, Attribute.thermal_damage: 63000, Attribute.kinetic_damage: 74000,
            Attribute.explosive_damage: 85000, self.cycle_attr.id: 250000
        }, effects=[self.effect], default_effect=self.effect).id, state=State.active)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 52000)
        self.assertAlmostEqual(volley.thermal, 63000)
        self.assertAlmostEqual(volley.kinetic, 74000)
        self.assertAlmostEqual(volley.explosive, 85000)
        self.assertAlmostEqual(volley.total, 274000)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_volley_multiplier(self):
        self.ch.attribute(attribute_id=Attribute.damage_multiplier)
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.em_damage: 52000, Attribute.thermal_damage: 63000, Attribute.kinetic_damage: 74000,
            Attribute.explosive_damage: 85000, self.cycle_attr.id: 250000, Attribute.damage_multiplier: 5.5
        }, effects=[self.effect], default_effect=self.effect).id, state=State.active)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertAlmostEqual(volley.em, 52000)
        self.assertAlmostEqual(volley.thermal, 63000)
        self.assertAlmostEqual(volley.kinetic, 74000)
        self.assertAlmostEqual(volley.explosive, 85000)
        self.assertAlmostEqual(volley.total, 274000)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_volley_insufficient_state(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.em_damage: 52000, Attribute.thermal_damage: 63000, Attribute.kinetic_damage: 74000,
            Attribute.explosive_damage: 85000, self.cycle_attr.id: 250000
        }, effects=[self.effect], default_effect=self.effect).id, state=State.online)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_volley_disabled_effect(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.em_damage: 52000, Attribute.thermal_damage: 63000, Attribute.kinetic_damage: 74000,
            Attribute.explosive_damage: 85000, self.cycle_attr.id: 250000
        }, effects=[self.effect], default_effect=self.effect).id, state=State.active)
        item._set_effect_activability(self.effect.id, False)
        fit.modules.high.append(item)
        # Verification
        volley = item.get_nominal_volley()
        self.assertIsNone(volley.em)
        self.assertIsNone(volley.thermal)
        self.assertIsNone(volley.kinetic)
        self.assertIsNone(volley.explosive)
        self.assertIsNone(volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_dps_no_reload(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.em_damage: 52000, Attribute.thermal_damage: 63000, Attribute.kinetic_damage: 74000,
            Attribute.explosive_damage: 85000, self.cycle_attr.id: 250000
        }, effects=[self.effect], default_effect=self.effect).id, state=State.active)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_nominal_dps(reload=False)
        self.assertAlmostEqual(dps.em, 208)
        self.assertAlmostEqual(dps.thermal, 252)
        self.assertAlmostEqual(dps.kinetic, 296)
        self.assertAlmostEqual(dps.explosive, 340)
        self.assertAlmostEqual(dps.total, 1096)
        # Cleanup
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_nominal_dps_reload(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(attributes={
            Attribute.em_damage: 52000, Attribute.thermal_damage: 63000, Attribute.kinetic_damage: 74000,
            Attribute.explosive_damage: 85000, self.cycle_attr.id: 250000
        }, effects=[self.effect], default_effect=self.effect).id, state=State.active)
        fit.modules.high.append(item)
        # Verification
        dps = item.get_nominal_dps(reload=True)
        self.assertAlmostEqual(dps.em, 208)
        self.assertAlmostEqual(dps.thermal, 252)
        self.assertAlmostEqual(dps.kinetic, 296)
        self.assertAlmostEqual(dps.explosive, 340)
        self.assertAlmostEqual(dps.total, 1096)
        # Cleanup
        self.assertEqual(len(self.log), 2)
        self.assert_fit_buffers_empty(fit)