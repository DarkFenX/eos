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


from .base import HolderContainerBase


class HolderList(HolderContainerBase):
    """
    Ordered container for holders.

    Positional arguments:
    fit -- fit, to which container is attached
    holderClass -- class, which will be instantiated
    when new holders are generated by means of container.
    """

    def __init__(self, fit, holderClass):
        self.__list = []
        HolderContainerBase.__init__(self, fit, holderClass)

    def insert(self, index, value):
        """
        Insert holder to given position; if position is
        out of range of container, fill it with Nones up
        to position and put holder there.

        Positional arguments:
        index -- position to take
        value -- can be holder or typeID, which is used
        to generate new holder

        Return value:
        Holder which was inserted to container.
        """
        holder = self.new(value)
        self._allocate(index - 1)
        self.__list.insert(index, holder)
        self._handleAdd(holder)
        return holder

    def append(self, value):
        """
        Append holder to the end of container.

        Positional arguments:
        value -- can be holder or typeID, which is used
        to generate new holder

        Return value:
        Holder which was appended to container.
        """
        holder = self.new(value)
        self.__list.append(holder)
        self._handleAdd(holder)
        return holder

    def remove(self, value):
        """
        Remove holder from container. Also clean container's
        tail if it's filled with Nones.

        Positional arguments:
        value -- holder or index of holder to remove
        """
        if isinstance(value, int):
            index = value
            holder = self.__list[index]
        else:
            holder = value
            index = self.__list.index(holder)
        self._handleRemove(self, holder)
        del self.__list[index]
        self._cleanup()

    def place(self, index, value):
        """
        Put holder to given position; if position is taken
        by another holder, remove it before taking its place;
        if position is out of range of container, fill it with
        Nones up to position and put holder there.

        Positional arguments:
        index -- position to take
        value -- can be holder or typeID, which is used
        to generate new holder

        Return value:
        Holder which was placed to container.
        """
        newHolder = self.new(value)
        try:
            oldHolder = self.__list[index]
        except IndexError:
            self._allocate(index)
        else:
            self._handleRemove(self, oldHolder)
        self.__list[index] = newHolder
        self._handleAdd(newHolder)
        return newHolder

    def fill(self, value):
        """
        Put holder to first free slot in container; if
        container doesn't have free slots, append holder
        to the end of container.

        Positional arguments:
        index -- position to take
        value -- can be holder or typeID, which is used
        to generate new holder

        Return value:
        Holder which was placed to container.
        """
        holder = self.new(value)
        try:
            index = self.__list.index(None)
        except ValueError:
            self.__list.append(holder)
        else:
            self.__list[index] = holder
        self._handleAdd(holder)
        return holder

    def free(self, value):
        """
        Free holder's slot (replace it with None). Also
        clean container's tail if it's filled with Nones.

        Positional arguments:
        value -- holder or index of slot to free
        """
        if isinstance(value, int):
            index = value
            holder = self.__list[index]
            if holder is None:
                return
        else:
            holder = value
            index = self.__list.index(holder)
        self._handleRemove(self, holder)
        self.__list[index] = None
        self._cleanup()

    def clear(self):
        """Remove everything from container."""
        for holder in self.__list:
            if holder is not None:
                self._handleRemove(holder)
        self.__list.clear()

    def __getitem__(self, index):
        """Get holder by index."""
        return self.__list[index]

    def index(self, holder):
        """Get index by holder."""
        return self.__list.index(holder)

    def __iter__(self):
        return iter(self.__list)

    def __contains__(self, holder):
        return holder in self.__list

    def __len__(self):
        return len(self.__list)

    def _allocate(self, index):
        """
        If passed index is out of range, complete
        list with Nones until index becomes available.
        """
        allocatedNum = len(self.__list)
        for _ in range(max(index - allocatedNum + 1, 0)):
            self.__list.append(None)

    def _cleanup(self):
        """Remove trailing Nones from list."""
        try:
            while self.__list[-1] is None:
                del self.__list[-1]
        # If we get IndexError, we've ran out of list elements
        # and we're fine with it
        except IndexError:
            pass
