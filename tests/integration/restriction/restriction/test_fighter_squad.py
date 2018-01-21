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


from eos import FighterSquad
from eos import Restriction
from eos import Ship
from eos.const.eve import AttrId
from tests.integration.restriction.testcase import RestrictionTestCase


class TestFighterSquad(RestrictionTestCase):
    """Check functionality of fighter squad quantity restriction."""

    def setUp(self):
        RestrictionTestCase.setUp(self)
        self.mkattr(attr_id=AttrId.fighter_tubes)

    def test_fail_excess_single(self):
        # Check that error is raised when quantity of used tubes exceeds tube
        # quantity provided by ship
        self.fit.ship = Ship(self.mktype(attrs={AttrId.fighter_tubes: 0}).id)
        item = FighterSquad(self.mktype().id)
        self.fit.fighters.add(item)
        # Action
        error = self.get_error(item, Restriction.fighter_squad)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_single_no_ship(self):
        # When stats module does not specify total tube quantity, make sure it's
        # assumed to be 0
        item = FighterSquad(self.mktype().id)
        self.fit.fighters.add(item)
        # Action
        error = self.get_error(item, Restriction.fighter_squad)
        # Verification
        self.assertIsNotNone(error)
        self.assertEqual(error.used, 1)
        self.assertEqual(error.total, 0)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_fail_excess_multiple(self):
        # Check that error works for multiple items
        self.fit.ship = Ship(self.mktype(attrs={AttrId.fighter_tubes: 1}).id)
        item1 = FighterSquad(self.mktype().id)
        item2 = FighterSquad(self.mktype().id)
        self.fit.fighters.add(item1)
        self.fit.fighters.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.fighter_squad)
        # Verification
        self.assertIsNotNone(error1)
        self.assertEqual(error1.used, 2)
        self.assertEqual(error1.total, 1)
        # Action
        error2 = self.get_error(item2, Restriction.fighter_squad)
        # Verification
        self.assertIsNotNone(error2)
        self.assertEqual(error2.used, 2)
        self.assertEqual(error2.total, 1)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_equal(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.fighter_tubes: 2}).id)
        item1 = FighterSquad(self.mktype().id)
        item2 = FighterSquad(self.mktype().id)
        self.fit.fighters.add(item1)
        self.fit.fighters.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.fighter_squad)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.fighter_squad)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_greater(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.fighter_tubes: 5}).id)
        item1 = FighterSquad(self.mktype().id)
        item2 = FighterSquad(self.mktype().id)
        self.fit.fighters.add(item1)
        self.fit.fighters.add(item2)
        # Action
        error1 = self.get_error(item1, Restriction.fighter_squad)
        # Verification
        self.assertIsNone(error1)
        # Action
        error2 = self.get_error(item2, Restriction.fighter_squad)
        # Verification
        self.assertIsNone(error2)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)

    def test_pass_no_source(self):
        self.fit.ship = Ship(self.mktype(attrs={AttrId.fighter_tubes: 0}).id)
        item = FighterSquad(self.mktype().id)
        self.fit.fighters.add(item)
        self.fit.source = None
        # Action
        error = self.get_error(item, Restriction.fighter_squad)
        # Verification
        self.assertIsNone(error)
        # Cleanup
        self.assert_fit_buffers_empty(self.fit)
        self.assertEqual(len(self.get_log()), 0)
