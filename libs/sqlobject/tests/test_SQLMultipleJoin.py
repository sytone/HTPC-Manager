from sqlobject import *
from sqlobject.tests.dbtest import *

class Race(SQLObject):
    name = StringCol()
    fightersAsList = MultipleJoin('RFighter', joinColumn="rf_id")
    fightersAsSResult = SQLMultipleJoin('RFighter', joinColumn="rf_id")

class RFighter(SQLObject):
    name = StringCol()
    race = ForeignKey('Race', dbName="rf_id")
    power = IntCol()

def createAllTables():
    setupClass([Race, RFighter])

def test_1():
    createAllTables()
    # create some races
    human=Race(name='human')
    saiyajin=Race(name='saiyajin')
    hibrid=Race(name='hibrid (human with sayajin)')
    namek=Race(name='namekuseijin')
    # create some fighters
    gokou=RFighter(name='Gokou (Kakaruto)', race=saiyajin, power=10)
    vegeta=RFighter(name='Vegeta', race=saiyajin, power=9)
    krilim=RFighter(name='Krilim', race=human, power=3)
    yancha=RFighter(name='Yancha', race=human, power=2)
    jackiechan=RFighter(name='Jackie Chan', race=human, power=2)
    gohan=RFighter(name='Gohan', race=hibrid, power=8)
    goten=RFighter(name='Goten', race=hibrid, power=7)
    trunks=RFighter(name='Trunks', race=hibrid, power=8)
    picollo=RFighter(name='Picollo', race=namek, power=6)
    neil=RFighter(name='Neil', race=namek, power=5)

    # testing the SQLMultipleJoin stuff
    for i, j in zip(human.fightersAsList, human.fightersAsSResult):
        assert i is j # the 2 ways should give the same result
    assert namek.fightersAsSResult.count() == len(namek.fightersAsList)
    assert saiyajin.fightersAsSResult.max('power') == 10
    assert trunks in hibrid.fightersAsSResult
    assert picollo not in hibrid.fightersAsSResult
    assert str(hibrid.fightersAsSResult.sum('power')) == '23'

def test_multiple_join_transaction():
    if not supports('transactions'):
        return
    createAllTables()
    trans = Race._connection.transaction()
    try:
        namek=Race(name='namekuseijin', connection=trans)
        gokou=RFighter(name='Gokou (Kakaruto)', race=namek, power=10, connection=trans)
        assert namek.fightersAsSResult.count() == 1
        assert namek.fightersAsSResult[0]._connection == trans
    finally:
        Race._connection.autoCommit = True