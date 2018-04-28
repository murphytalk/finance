from finance.common.utils import get_valid_db_from_env
from sqlalchemy import create_engine, Column, String, Float, Integer, ForeignKey
from sqlalchemy.ext.automap import automap_base, relationship
from sqlalchemy.orm import sessionmaker

DATABASE = get_valid_db_from_env('FINANCE_DB')
Base = automap_base()

# Overriding Naming Schemes to avoid error :
# WARNING: when configuring property 'broker' on Mapper|instrument|instrument, column 'broker' conflicts with property '<RelationshipProperty at 0x7f1b12d1a2c8; broker>'.
# see http://docs.sqlalchemy.org/en/rel_1_0/orm/extensions/automap.html#overriding-naming-schemes
# see https://bitbucket.org/zzzeek/sqlalchemy/issues/3449/automap_base-fails-on-my-database
def name_for_scalar_relationship(base, local_cls, referred_cls, constraint):
    return referred_cls.__name__.lower() + "_ref"

#class Instrument(Base):
#    __tablename__ = 'instrument'
#
#    # override schema elements like Columns
#    name = Column('name', String)
#
#    instrument_type = relationship("instrument_type", collection_class=set)
#    broker_id = Column(Integer, ForeignKey('broker.id'))
#    broker = relationship("broker", collection_class=set)
#    currency = relationship("currency", collection_class=set)
#    url = Column('url', String)
#    expense = Column('expsens_ratio', Float)


engine = create_engine("sqlite:///%s" % DATABASE if DATABASE else ":memory:")
Base.prepare(engine, reflect=True, name_for_scalar_relationship=name_for_scalar_relationship)

Session = sessionmaker()
Session.configure(bind=engine)
session = Session()

Broker = Base.classes.broker
Currency = Base.classes.currency
Country = Base.classes.country
Asset = Base.classes.asset
InstrumentType = Base.classes.instrument_type
#AssetAllocation = Base.classes.asset_allocation
#CountryAllocation = Base.classes.country_allocation
Region = Base.classes.region
#Regions = Base.classes.regions
Filter = Base.classes.filter
#InstrumentFilter = Base.classes.instrument_filter
#Cash = Base.classes.cash
Instrument = Base.classes.instrument
#for k,v in Base.classes.items():
#    print(k,v)



