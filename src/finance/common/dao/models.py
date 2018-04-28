from sqlalchemy import create_engine, Column, String, Float, Integer, ForeignKey
from sqlalchemy.ext.automap import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from finance.common.utils import get_valid_db_from_env

DATABASE = get_valid_db_from_env('FINANCE_DB')
Base = declarative_base()


class Broker(Base):
    __tablename__ = "broker"

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    full_name = Column('fullName', String)

    def __repr__(self):
        return self.full_name


class Country(Base):
    __tablename__ = "country"

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)

    def __repr__(self):
        return self.name


class Currency(Base):
    __tablename__ = "currency"

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)

    def __repr__(self):
        return self.name


class Asset(Base):
    __tablename__ = "asset"

    id = Column('id', Integer, primary_key=True)
    asset_type = Column('type', String)

    def __repr__(self):
        return self.asset_type


class InstrumentType(Base):
    __tablename__ = "instrument_type"

    id = Column('id', Integer, primary_key=True)
    instrument_type = Column('type', String)

    def __repr__(self):
        return self.instrument_type


class Instrument(Base):
    __tablename__ = 'instrument'

    id = Column('id', Integer, primary_key=True)
    # override schema elements like Columns
    name = Column('name', String)

    instrument_type_id = Column('type', Integer, ForeignKey('instrument_type.id'))
    instrument_type = relationship("InstrumentType", backref='instrument')

    broker_id = Column('broker', Integer, ForeignKey('broker.id'))
    broker = relationship("Broker", backref='instrument')

    currency_id = Column('currency', Integer, ForeignKey('currency.id'))
    currency = relationship("Currency", backref='instrument')

    url = Column('url', String)
    expense = Column('expense_ratio', Float)

    def __repr__(self):
        return self.name


def map_models():
    engine = create_engine("sqlite:///%s" % DATABASE if DATABASE else "sqlite://")
    session = sessionmaker()
    session.configure(bind=engine)
    return session()
