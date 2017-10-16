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


from collections import namedtuple

from eos.const.eos import Restriction, State
from eos.fit.pubsub.message import InstrStatesActivate, InstrStatesDeactivate
from .base import BaseRestrictionRegister
from ..exception import RestrictionValidationError


StateErrorData = namedtuple(
    'StateErrorData', ('current_state', 'allowed_states'))


class StateRestrictionRegister(BaseRestrictionRegister):
    """Make sure items' states are consistent.

    I.e. check that passive modules are not active, etc.
    """

    def __init__(self, msg_broker):
        self.__items = set()
        msg_broker._subscribe(self, self._handler_map.keys())

    def _handle_item_states_activation(self, message):
        if State.online in message.states:
            self.__items.add(message.item)

    def _handle_item_states_deactivation(self, message):
        if State.online in message.states:
            self.__items.discard(message.item)

    _handler_map = {
        InstrStatesActivate: _handle_item_states_activation,
        InstrStatesDeactivate: _handle_item_states_deactivation}

    def validate(self):
        tainted_items = {}
        for item in self.__items:
            if item.state > item._eve_type.max_state:
                allowed_states = tuple(
                    s for s in State if s <= item._eve_type.max_state)
                tainted_items[item] = StateErrorData(
                    current_state=item.state,
                    allowed_states=allowed_states)
        if tainted_items:
            raise RestrictionValidationError(tainted_items)

    @property
    def type(self):
        return Restriction.state
