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
from eos.const.eos import ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestTgtItemDomainShip(CalculatorTestCase):

    def setUp(self):
        super().setUp()
        self.tgt_attr = self.ch.attribute()
        src_attr = self.ch.attribute()
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.ship,
            tgt_attr=self.tgt_attr.id,
            operator=ModifierOperator.post_percent,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=(modifier,))
        self.influence_source = Implant(self.ch.type(effects=(effect,), attributes={src_attr.id: 20}).id)

    def test_ship(self):
        influence_target = Ship(self.ch.type(attributes={self.tgt_attr.id: 100}).id)
        self.fit.ship = influence_target
        # Action
        self.fit.implants.add(self.influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 120)
        # Action
        self.fit.implants.remove(self.influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.ship = None
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)

    def test_parent_domain_ship(self):
        influence_target = Rig(self.ch.type(attributes={self.tgt_attr.id: 100}).id)
        self.fit.rigs.add(influence_target)
        # Action
        self.fit.implants.add(self.influence_source)
        # Verification
        self.assertAlmostEqual(influence_target.attributes[self.tgt_attr.id], 100)
        # Cleanup
        self.fit.implants.remove(self.influence_source)
        self.fit.rigs.remove(influence_target)
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(self.fit)