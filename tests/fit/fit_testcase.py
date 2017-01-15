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


from tests.eos_testcase import EosTestCase
from .environment import FitAssertionChecks


class FitTestCase(EosTestCase):
    """
    Additional functionality provided:

    self.assert_fit_buffers_empty -- checks if fit has any
    holders assigned to it
    self.run_fit_assertions -- returns context manager which
    turns on on-fit per-message type assertions
    """

    def assert_fit_buffers_empty(self, fit):
        holder_num = 0
        # Check if we have anything in our single holder storages
        single_holders = ('character', 'ship', 'stance', 'effect_beacon')
        for attr_name in single_holders:
            holder = getattr(fit, attr_name, None)
            if holder is not None:
                holder_num += 1
        # Seek for multiple holder storages
        for attr_name in dir(fit):
            if attr_name.startswith("__") and attr_name.endswith("__"):
                continue
            if attr_name in ('message_store', '_message_assertions', '_handler_map', '_MessageBroker__subscribers'):
                continue
            attr_val = getattr(fit, attr_name)
            try:
                attr_len = len(attr_val)
            except TypeError:
                pass
            else:
                holder_num += attr_len
        if holder_num > 0:
            plu = 'y' if holder_num == 1 else 'ies'
            msg = '{} entr{} in buffers: buffers must be empty'.format(holder_num, plu)
            self.fail(msg=msg)

    def run_fit_assertions(self, fit):
        return FitAssertionChecks(fit)
