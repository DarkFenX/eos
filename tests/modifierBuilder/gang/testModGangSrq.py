#===============================================================================
# Copyright (C) 2011 Diego Duclos
# Copyright (C) 2011-2012 Anton Vorobyov
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


from eos.const import State, Location, EffectBuildStatus, Context, FilterType, Operator
from eos.eve.effect import Effect
from eos.eve.expression import Expression
from eos.fit.attributeCalculator.modifier.modifierBuilder import ModifierBuilder
from eos.tests.environment import Logger
from eos.tests.eosTestCase import EosTestCase
from eos.tests.modifierBuilder.environment import callize


class TestModGangSrq(EosTestCase):
    """Test parsing of trees describing gang-mates' ship modules modification filtered by skill requirement"""

    def setUp(self):
        EosTestCase.setUp(self)
        eTgtSrq = Expression(None, 29, expressionTypeId=3435)
        eTgtAttr = Expression(None, 22, expressionAttributeId=54)
        eOptr = Expression(None, 21, value="PostPercent")
        eSrcAttr = Expression(None, 22, expressionAttributeId=833)
        eTgtSpec = Expression(None, 64, arg1=eTgtSrq, arg2=eTgtAttr)
        eOptrTgt = Expression(None, 31, arg1=eOptr, arg2=eTgtSpec)
        self.eAddMod = Expression(1, 5, arg1=eOptrTgt, arg2=eSrcAttr)
        self.eRmMod = Expression(2, 57, arg1=eOptrTgt, arg2=eSrcAttr)

    def testGenericBuildSuccess(self):
        effect = Effect(None, 0, preExpressionCallData=callize(self.eAddMod), postExpressionCallData=callize(self.eRmMod))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.context, Context.gang)
        self.assertEqual(modifier.sourceAttributeId, 833)
        self.assertEqual(modifier.operator, Operator.postPercent)
        self.assertEqual(modifier.targetAttributeId, 54)
        self.assertEqual(modifier.location, Location.ship)
        self.assertEqual(modifier.filterType, FilterType.skill)
        self.assertEqual(modifier.filterValue, 3435)

    def testEffCategoryPassive(self):
        effect = Effect(None, 0, preExpressionCallData=callize(self.eAddMod), postExpressionCallData=callize(self.eRmMod))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.context, Context.gang)

    def testEffCategoryActive(self):
        effect = Effect(None, 1, preExpressionCallData=callize(self.eAddMod), postExpressionCallData=callize(self.eRmMod))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.active)
        self.assertEqual(modifier.context, Context.gang)

    def testEffCategoryTarget(self):
        effect = Effect(None, 2, preExpressionCallData=callize(self.eAddMod), postExpressionCallData=callize(self.eRmMod))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)

    def testEffCategoryArea(self):
        effect = Effect(None, 3, preExpressionCallData=callize(self.eAddMod), postExpressionCallData=callize(self.eRmMod))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)

    def testEffCategoryOnline(self):
        effect = Effect(None, 4, preExpressionCallData=callize(self.eAddMod), postExpressionCallData=callize(self.eRmMod))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.online)
        self.assertEqual(modifier.context, Context.gang)

    def testEffCategoryOverload(self):
        effect = Effect(None, 5, preExpressionCallData=callize(self.eAddMod), postExpressionCallData=callize(self.eRmMod))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.overload)
        self.assertEqual(modifier.context, Context.gang)

    def testEffCategoryDungeon(self):
        effect = Effect(None, 6, preExpressionCallData=callize(self.eAddMod), postExpressionCallData=callize(self.eRmMod))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.error)
        self.assertEqual(len(modifiers), 0)

    def testEffCategorySystem(self):
        effect = Effect(None, 7, preExpressionCallData=callize(self.eAddMod), postExpressionCallData=callize(self.eRmMod))
        modifiers, status = ModifierBuilder.build(effect, Logger())
        self.assertEqual(status, EffectBuildStatus.okFull)
        self.assertEqual(len(modifiers), 1)
        modifier = modifiers[0]
        self.assertEqual(modifier.state, State.offline)
        self.assertEqual(modifier.context, Context.gang)