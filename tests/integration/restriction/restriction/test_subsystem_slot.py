# ==============================================================================
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
# ==============================================================================


from eos import Restriction
from eos import Ship
from eos import Subsystem
from eos.const.eve import AttrId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestSubsystemSlot(RestrictionTestCase):
    """Check functionality of subsystem slot quantity restriction."""

    def setUp(self):
        RestrictionTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.max_subsystems)

    def test_fail_single(self):
        # Check that error is raised when quantity of used slots exceeds slot
        # quantity provided by ship
        self.fit.ship = Ship(self.mktype(attrs={AttrId.max_subsystems: 0}).id)
        item = Subsystem(self.mktype().id)
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.subsystem_slot)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_multiple(self):
        # Check that error works for multiple items
        self.fit.ship = Ship(self.mktype(attrs={AttrId.max_subsystems: 1}).id)
        item_type = self.mktype()
        item1 = Subsystem(item_type.id)
        item2 = Subsystem(item_type.id)
        self.fit.subsystems.add(item1)
        self.fit.subsystems.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.subsystem_slot)
        # Verification
        self.assertIsNotNone(error1)
        self.assertEqual(error1.used, 2)
        self.assertEqual(error1.total, 1)
        # Action
        error2 = self.get_error(item2, Restriction.subsystem_slot)
        # Verification
        self.assertIsNotNone(error2)
        self.assertEqual(error2.used, 2)
        self.assertEqual(error2.total, 1)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_item_not_loaded(self):
        # Item still counts even when it's not loaded
        self.fit.ship = Ship(self.mktype(attrs={AttrId.max_subsystems: 0}).id)
        item = Subsystem(self.allocate_type_id())
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.subsystem_slot)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_absent(self):
        # When stats module does not specify total slot quantity, make sure it's
        # assumed to be 0
        item = Subsystem(self.mktype().id)
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.subsystem_slot)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_attr_absent(self):
        self.fit.ship = Ship(self.mktype().id)
        item = Subsystem(self.mktype().id)
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.subsystem_slot)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_ship_not_loaded(self):
        self.fit.ship = Ship(self.allocate_type_id())
        item = Subsystem(self.mktype().id)
        self.fit.subsystems.add(item)
        # Action
        error = self.get_error(item, Restriction.subsystem_slot)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_equal(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.max_subsystems: 2}).id)
        item_type = self.mktype()
        item1 = Subsystem(item_type.id)
        item2 = Subsystem(item_type.id)
        self.fit.subsystems.add(item1)
        self.fit.subsystems.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.subsystem_slot)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.subsystem_slot)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_greater(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.max_subsystems: 5}).id)
        item_type = self.mktype()
        item1 = Subsystem(item_type.id)
        item2 = Subsystem(item_type.id)
        self.fit.subsystems.add(item1)
        self.fit.subsystems.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.subsystem_slot)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.subsystem_slot)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
