from unittest.mock import Mock

from eos.const.eos import Location, State
from eos.const.eve import Attribute
from eos.fit.holder.item import Drone, Ship, Implant
from eos.tests.statTracker.statTestCase import StatTestCase


class TestDroneBandwidth(StatTestCase):
    """Check functionality of drrone bandwidth stats"""

    def testOutput(self):
        # Check that modified attribute of ship is used
        shipItem = self.ch.type_(typeId=1, attributes={Attribute.droneBandwidth: 10})
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {Attribute.droneBandwidth: 50}
        self.setShip(shipHolder)
        self.assertEqual(self.st.droneBandwidth.output, 50)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoShip(self):
        # None for output when no ship
        self.assertIsNone(self.st.droneBandwidth.output)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testOutputNoAttr(self):
        # None for output when no attribute on ship
        shipItem = self.ch.type_(typeId=1)
        shipHolder = Mock(state=State.offline, item=shipItem, _location=None, spec_set=Ship)
        shipHolder.attributes = {}
        self.setShip(shipHolder)
        self.assertIsNone(self.st.droneBandwidth.output)
        self.setShip(None)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseSingle(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.droneBandwidthUsed: 0})
        holder = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        holder.attributes = {Attribute.droneBandwidthUsed: 50}
        self.trackHolder(holder)
        self.assertEqual(self.st.droneBandwidth.used, 50)
        self.untrackHolder(holder)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseMultiple(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.droneBandwidthUsed: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        holder1.attributes = {Attribute.droneBandwidthUsed: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        holder2.attributes = {Attribute.droneBandwidthUsed: 30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.droneBandwidth.used, 80)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseNegative(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.droneBandwidthUsed: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        holder1.attributes = {Attribute.droneBandwidthUsed: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        holder2.attributes = {Attribute.droneBandwidthUsed: -30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.droneBandwidth.used, 20)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseNone(self):
        self.assertEqual(self.st.droneBandwidth.used, 0)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseState(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.droneBandwidthUsed: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        holder1.attributes = {Attribute.droneBandwidthUsed: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.offline, item=item, _location=Location.space, spec_set=Drone)
        holder2.attributes = {Attribute.droneBandwidthUsed: 30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.droneBandwidth.used, 50)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()

    def testUseOtherClassLocation(self):
        item = self.ch.type_(typeId=1, attributes={Attribute.droneBandwidthUsed: 0})
        holder1 = Mock(state=State.online, item=item, _location=Location.space, spec_set=Drone)
        holder1.attributes = {Attribute.droneBandwidthUsed: 50}
        self.trackHolder(holder1)
        holder2 = Mock(state=State.online, item=item, _location=Location.character, spec_set=Implant)
        holder2.attributes = {Attribute.droneBandwidthUsed: 30}
        self.trackHolder(holder2)
        self.assertEqual(self.st.droneBandwidth.used, 80)
        self.untrackHolder(holder1)
        self.untrackHolder(holder2)
        self.assertEqual(len(self.log), 0)
        self.assertStatBuffersEmpty()
