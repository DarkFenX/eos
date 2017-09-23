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
from eos.const.eve import Attribute, Effect, EffectCategory
from eos.data.cachable.modifier import DogmaModifier
from tests.integration.stats.stat_testcase import StatTestCase


class TestStatsDamageVolley(StatTestCase):

    def setUp(self):
        super().setUp()
        self.ch.attribute(attribute_id=Attribute.em_damage)
        self.ch.attribute(attribute_id=Attribute.thermal_damage)
        self.ch.attribute(attribute_id=Attribute.kinetic_damage)
        self.ch.attribute(attribute_id=Attribute.explosive_damage)
        self.ch.attribute(attribute_id=Attribute.damage_multiplier)
        self.dd_effect = self.ch.effect(
            effect_id=Effect.projectile_fired, category=EffectCategory.active
        )

    def test_empty(self):
        fit = Fit()
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertIsNone(stats_volley.total)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_single(self):
        src_attr = self.ch.attribute()
        modifier = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=Attribute.damage_multiplier,
            operator=ModifierOperator.post_mul,
            src_attr=src_attr.id
        )
        effect = self.ch.effect(category=EffectCategory.passive, modifiers=[modifier])
        fit = Fit()
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2, src_attr.id: 1.5},
            effects=(self.dd_effect, effect), default_effect=self.dd_effect
        ).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.explosive_damage: 9.6
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 3.6)
        self.assertAlmostEqual(stats_volley.thermal, 7.2)
        self.assertAlmostEqual(stats_volley.kinetic, 14.4)
        self.assertAlmostEqual(stats_volley.explosive, 28.8)
        self.assertAlmostEqual(stats_volley.total, 54)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_multiple(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item1.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.explosive_damage: 9.6
        }).id)
        fit.modules.high.append(item1)
        item2 = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item2.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 12, Attribute.thermal_damage: 24,
            Attribute.kinetic_damage: 48, Attribute.explosive_damage: 96
        }).id)
        fit.modules.high.append(item2)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 26.4)
        self.assertAlmostEqual(stats_volley.thermal, 52.8)
        self.assertAlmostEqual(stats_volley.kinetic, 105.6)
        self.assertAlmostEqual(stats_volley.explosive, 211.2)
        self.assertAlmostEqual(stats_volley.total, 396)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_arguments_custom_profile(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.explosive_damage: 9.6
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_volley = fit.stats.get_nominal_volley(target_resistances=ResistanceProfile(0, 1, 1, 1))
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertAlmostEqual(stats_volley.thermal, 0)
        self.assertAlmostEqual(stats_volley.kinetic, 0)
        self.assertAlmostEqual(stats_volley.explosive, 0)
        self.assertAlmostEqual(stats_volley.total, 2.4)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_arguments_custom_filter(self):
        fit = Fit()
        item1 = ModuleHigh(self.ch.type(
            group=55, attributes={Attribute.damage_multiplier: 2},
            effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item1.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.explosive_damage: 9.6
        }).id)
        fit.modules.high.append(item1)
        item2 = ModuleHigh(self.ch.type(
            group=54, attributes={Attribute.damage_multiplier: 2},
            effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item2.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 12, Attribute.thermal_damage: 24,
            Attribute.kinetic_damage: 48, Attribute.explosive_damage: 96
        }).id)
        fit.modules.high.append(item2)
        # Action
        stats_volley = fit.stats.get_nominal_volley(item_filter=lambda i: i._eve_type.group == 55)
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertAlmostEqual(stats_volley.thermal, 4.8)
        self.assertAlmostEqual(stats_volley.kinetic, 9.6)
        self.assertAlmostEqual(stats_volley.explosive, 19.2)
        self.assertAlmostEqual(stats_volley.total, 36)
        # Cleanup
        self.assertEqual(len(self.log), 0)
        self.assert_fit_buffers_empty(fit)

    def test_single_none_em(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.thermal_damage: 2.4, Attribute.kinetic_damage: 4.8,
            Attribute.explosive_damage: 9.6
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertAlmostEqual(stats_volley.thermal, 4.8)
        self.assertAlmostEqual(stats_volley.kinetic, 9.6)
        self.assertAlmostEqual(stats_volley.explosive, 19.2)
        self.assertAlmostEqual(stats_volley.total, 33.6)
        # Cleanup
        # Failure to fetch damage value is not issue for this test
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_single_none_therm(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.kinetic_damage: 4.8,
            Attribute.explosive_damage: 9.6
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertIsNone(stats_volley.thermal)
        self.assertAlmostEqual(stats_volley.kinetic, 9.6)
        self.assertAlmostEqual(stats_volley.explosive, 19.2)
        self.assertAlmostEqual(stats_volley.total, 31.2)
        # Cleanup
        # Failure to fetch damage value is not issue for this test
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_single_none_kin(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.explosive_damage: 9.6
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertAlmostEqual(stats_volley.thermal, 4.8)
        self.assertIsNone(stats_volley.kinetic)
        self.assertAlmostEqual(stats_volley.explosive, 19.2)
        self.assertAlmostEqual(stats_volley.total, 26.4)
        # Cleanup
        # Failure to fetch damage value is not issue for this test
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_single_none_expl(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8
        }).id)
        fit.modules.high.append(item)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertAlmostEqual(stats_volley.thermal, 4.8)
        self.assertAlmostEqual(stats_volley.kinetic, 9.6)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 16.8)
        # Cleanup
        # Failure to fetch damage value is not issue for this test
        self.assertEqual(len(self.log), 1)
        self.assert_fit_buffers_empty(fit)

    def test_single_none_all(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item.charge = Charge(self.ch.type().id)
        fit.modules.high.append(item)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertIsNone(stats_volley.total)
        # Cleanup
        # Failure to fetch damage values is not issue for this test
        self.assertEqual(len(self.log), 4)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_em(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={Attribute.em_damage: 0}).id)
        fit.modules.high.append(item)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 0)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 0)
        # Cleanup
        # Failure to fetch damage values is not issue for this test
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_therm(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={Attribute.thermal_damage: 0}).id)
        fit.modules.high.append(item)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertAlmostEqual(stats_volley.thermal, 0)
        self.assertIsNone(stats_volley.kinetic)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 0)
        # Cleanup
        # Failure to fetch damage values is not issue for this test
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_kin(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={Attribute.kinetic_damage: 0}).id)
        fit.modules.high.append(item)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertAlmostEqual(stats_volley.kinetic, 0)
        self.assertIsNone(stats_volley.explosive)
        self.assertAlmostEqual(stats_volley.total, 0)
        # Cleanup
        # Failure to fetch damage values is not issue for this test
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_single_zero_expl(self):
        fit = Fit()
        item = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item.charge = Charge(self.ch.type(attributes={Attribute.explosive_damage: 0}).id)
        fit.modules.high.append(item)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertIsNone(stats_volley.em)
        self.assertIsNone(stats_volley.thermal)
        self.assertIsNone(stats_volley.kinetic)
        self.assertAlmostEqual(stats_volley.explosive, 0)
        self.assertAlmostEqual(stats_volley.total, 0)
        # Cleanup
        # Failure to fetch damage values is not issue for this test
        self.assertEqual(len(self.log), 3)
        self.assert_fit_buffers_empty(fit)

    def test_none_and_data(self):
        # As container for damage dealers is not ordered,
        # this test may be unreliable (even if there's issue,
        # it won't fail each run)
        fit = Fit()
        item1 = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item1.charge = Charge(self.ch.type(attributes={
            Attribute.em_damage: 1.2, Attribute.thermal_damage: 2.4,
            Attribute.kinetic_damage: 4.8, Attribute.explosive_damage: 9.6
        }).id)
        fit.modules.high.append(item1)
        item2 = ModuleHigh(self.ch.type(
            attributes={Attribute.damage_multiplier: 2}, effects=[self.dd_effect], default_effect=self.dd_effect
        ).id, state=State.active)
        item2.charge = Charge(self.ch.type().id)
        fit.modules.high.append(item2)
        # Action
        stats_volley = fit.stats.get_nominal_volley()
        # Verification
        self.assertAlmostEqual(stats_volley.em, 2.4)
        self.assertAlmostEqual(stats_volley.thermal, 4.8)
        self.assertAlmostEqual(stats_volley.kinetic, 9.6)
        self.assertAlmostEqual(stats_volley.explosive, 19.2)
        self.assertAlmostEqual(stats_volley.total, 36)
        # Cleanup
        self.assertEqual(len(self.log), 4)
        self.assert_fit_buffers_empty(fit)
