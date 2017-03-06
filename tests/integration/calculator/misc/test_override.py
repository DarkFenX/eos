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


from eos.const.eos import State, ModifierTargetFilter, ModifierDomain, ModifierOperator
from eos.const.eve import EffectCategory
from eos.data.cache_object.modifier import DogmaModifier
from eos.fit.message import AttrValueChangedMasked
from tests.integration.calculator.calculator_testcase import CalculatorTestCase


class TestOverride(CalculatorTestCase):
    """
    Check that attribute overriding functions as expected.
    """

    def setUp(self):
        super().setUp()
        self.attr1 = self.ch.attribute()
        self.attr2 = self.ch.attribute()
        self.attr3 = self.ch.attribute()
        self.attr4 = self.ch.attribute()
        modifier1 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.attr2.id,
            operator=ModifierOperator.post_percent,
            src_attr=self.attr1.id
        )
        modifier2 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.attr3.id,
            operator=ModifierOperator.post_percent,
            src_attr=self.attr2.id
        )
        modifier3 = DogmaModifier(
            tgt_filter=ModifierTargetFilter.item,
            tgt_domain=ModifierDomain.self,
            tgt_attr=self.attr4.id,
            operator=ModifierOperator.post_percent,
            src_attr=self.attr3.id
        )
        effect1 = self.ch.effect(category=EffectCategory.online)
        effect1.modifiers = (modifier1,)
        effect2 = self.ch.effect(category=EffectCategory.passive)
        effect2.modifiers = (modifier2, modifier3)
        self.item = IndependentItem(self.ch.type(effects=(effect1, effect2), attributes={self.attr1.id: 50, self.attr2.id: 100, self.attr3.id: 5, self.attr4.id: 50}).id)
        self.fit = Fit(self.ch, msgstore_filter=lambda m: (isinstance(m, AttrValueChangedMasked)))
        self.fit.items.add(self.item)

    def test_get(self):
        # Setup
        item = self.item
        self.assertAlmostEqual(item.attributes[self.attr4.id], 55)
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        messages_before = len(self.fit.message_store)
        # Action
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_get_ignored_overrides(self):
        # Setup
        item = self.item
        self.assertAlmostEqual(item.attributes[self.attr3.id], 10)
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        self.assertAlmostEqual(item.attributes._get_without_overrides(self.attr3.id), 10)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_override_arguments(self):
        # Setup
        item = self.item
        self.assertAlmostEqual(item.attributes[self.attr3.id], 10)
        # Action
        item.attributes._set_override_callback(self.attr3.id, (lambda x, y=2, z=33: x - y * z, (55,), {'y': 11}))
        # Verification
        self.assertAlmostEqual(item.attributes[self.attr3.id], -308)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_override_set(self):
        # Setup
        item = self.item
        self.assertAlmostEqual(item.attributes[self.attr3.id], 10)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 55)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes._get_without_overrides(self.attr3.id), 10)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_override_update(self):
        # Setup
        item = self.item
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes._set_override_callback(self.attr3.id, (lambda: 88, (), {}))
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 88)
        self.assertAlmostEqual(item.attributes._get_without_overrides(self.attr3.id), 10)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 94)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_override_delete(self):
        # Setup
        item = self.item
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes._del_override_callback(self.attr3.id)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 10)
        self.assertAlmostEqual(item.attributes._get_without_overrides(self.attr3.id), 10)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 55)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_delete_override_persistence(self):
        # Setup
        item = self.item
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        # We delete by putting attr3 under influence of another modifier
        item.state = State.online
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_delete_modified_removed(self):
        # Setup
        item = self.item
        self.assertAlmostEqual(item.attributes[self.attr3.id], 10)
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        # We delete by putting attr3 under influence of another modifier
        item.state = State.online
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChangedMasked))
        self.assertIs(message.item, self.item)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_delete_modified_unchanged(self):
        # Setup
        item = self.item
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        # We delete by putting attr3 under influence of another modifier
        item.state = State.online
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_clear_override_persistence(self):
        # Setup
        item = self.item
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes.clear()
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_clear_modified_removed(self):
        # Setup
        item = self.item
        self.assertAlmostEqual(item.attributes[self.attr3.id], 10)
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes.clear()
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 1)
        message = self.fit.message_store[-1]
        self.assertTrue(isinstance(message, AttrValueChangedMasked))
        self.assertIs(message.item, self.item)
        self.assertEqual(message.attr, self.attr3.id)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_clear_modified_unchanged(self):
        # Setup
        item = self.item
        item.attributes._set_override_callback(self.attr3.id, (lambda: 77, (), {}))
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        item.attributes.clear()
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 77)
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_changing_caching(self):
        # Setup
        func_data = [77]
        item = self.item
        self.assertAlmostEqual(item.attributes[self.attr4.id], 55)
        item.attributes._set_override_callback(self.attr3.id, (lambda: func_data[0], (), {}))
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        func_data[0] = 88
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        self.assertAlmostEqual(item.attributes[self.attr3.id], 88)
        # Without notification, dependency values stay the same
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)

    def test_changing_notification(self):
        # Setup
        func_data = [77]
        item = self.item
        self.assertAlmostEqual(item.attributes[self.attr4.id], 55)
        item.attributes._set_override_callback(self.attr3.id, (lambda: func_data[0], (), {}))
        self.assertAlmostEqual(item.attributes[self.attr4.id], 88.5)
        messages_before = len(self.fit.message_store)
        # Action
        func_data[0] = 88
        item.attributes._override_value_may_change(self.attr3.id)
        # Verification
        messages_after = len(self.fit.message_store)
        self.assertEqual(messages_after - messages_before, 0)
        # Cleaned up on notification & now recalculated
        self.assertAlmostEqual(item.attributes[self.attr4.id], 94)
        # Cleanup
        self.fit.items.remove(item)
        self.assert_fit_buffers_empty(self.fit)