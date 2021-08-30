import sqlalchemy.types as types
from sqlalchemy import create_engine, Column, String, Float, Integer, ForeignKey
from sqlalchemy.ext.automap import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

from finance.common.utils import get_valid_db_from_env, epoch2date, date2epoch

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


class Region(Base):
    __tablename__ = "region"

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)

    def __repr__(self):
        return self.name


class CountryByRegion(Base):
    __tablename__ = "regions"

    id = Column('ROWID', Integer, primary_key=True)

    country_id = Column('country', Integer, ForeignKey('country.id'))
    region_id = Column('region', Integer, ForeignKey('region.id'))

    country = relationship("Country", foreign_keys=[country_id], backref='regions')
    region = relationship("Region", foreign_keys=[region_id], backref='regions')

    def __repr__(self):
        return ("%s/%s") % (self.country, self.region)


class Asset(Base):
    __tablename__ = "asset"

    id = Column('id', Integer, primary_key=True)
    type = Column('type', String)

    def __repr__(self):
        return self.type


class InstrumentType(Base):
    __tablename__ = "instrument_type"

    id = Column('id', Integer, primary_key=True)
    type = Column('type', String)

    def __repr__(self):
        return self.type


class Instrument(Base):
    __tablename__ = 'instrument'

    id = Column('id', Integer, primary_key=True)
    # override schema elements like Columns
    name = Column('name', String)

    instrument_type_id = Column('type', Integer, ForeignKey('instrument_type.id'))
    instrument_type = relationship("InstrumentType", backref='instrument')

    currency_id = Column('currency', Integer, ForeignKey('currency.id'))
    currency = relationship("Currency", backref='instrument')

    url = Column('url', String)
    expense = Column('expense_ratio', Float)

    def __repr__(self):
        return self.name


class AssetAllocation(Base):
    __tablename__ = "asset_allocation"

    id = Column('ROWID', Integer, primary_key=True)
    instrument_id = Column('instrument', Integer, ForeignKey('instrument.id'))
    instrument = relationship("Instrument", backref='asset_allocation')

    asset_id = Column('asset', Integer, ForeignKey('asset.id'))
    asset = relationship("Asset")
    ratio = Column('ratio', Float)


class CountryAllocation(Base):
    __tablename__ = "country_allocation"

    id = Column('ROWID', Integer, primary_key=True)
    instrument_id = Column('instrument', Integer, ForeignKey('instrument.id'))
    instrument = relationship("Instrument", backref='country_allocation')

    country_id = Column('country', Integer, ForeignKey('country.id'))
    country = relationship("Country")
    ratio = Column('ratio', Float)


class MyEpochType(types.TypeDecorator):
    impl = types.Integer

    def process_bind_param(self, value, dialect):
        return date2epoch(value)

    def process_result_value(self, value, dialect):
        return epoch2date(value)


class FundPerformance(Base):
    __tablename__ = "fund"

    id = Column('ROWID', Integer, primary_key=True)
    instrument_id = Column('instrument', Integer, ForeignKey('instrument.id'))
    instrument = relationship("Instrument")

    broker_id = Column('broker', Integer, ForeignKey('broker.id'))
    broker = relationship("Broker", backref='funds')

    amount = Column(Integer)
    price = Column(Float)
    value = Column(Float)
    capital = Column(Float)
    profit = Column(Float)
    date = Column(MyEpochType)


class StockTransaction(Base):
    __tablename__ = "transaction"

    id = Column('ROWID', Integer, primary_key=True)
    instrument_id = Column('instrument', Integer, ForeignKey('instrument.id'))
    instrument = relationship("Instrument")

    broker_id = Column('broker', Integer, ForeignKey('broker.id'))
    broker = relationship("Broker", backref='transaction')

    type = Column(String)

    price = Column(Float)
    shares = Column(Float)
    fee = Column(Float)
    date = Column(MyEpochType)


class Quote(Base):
    __tablename__ = "quote"

    id = Column('ROWID', Integer, primary_key=True)
    instrument_id = Column('instrument', Integer, ForeignKey('instrument.id'))
    instrument = relationship("Instrument")

    price = Column(Float)
    date = Column(MyEpochType)


class Cash(Base):
    __tablename__ = "cash"

    id = Column('ROWID', Integer, primary_key=True)
    currency_id = Column('ccy', Integer, ForeignKey('currency.id'))
    currency = relationship('Currency')

    broker_id = Column('broker', Integer, ForeignKey('broker.id'))
    broker = relationship("Broker")

    balance = Column(Float)


class Portfolio(Base):
    __tablename__ = "portfolio"

    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return self.name


class PortfolioAllocation(Base):
    __tablename__ = "portfolio_allocation"

    id = Column(Integer, primary_key=True)

    portfolio_id = Column('portfolio', Integer, ForeignKey('portfolio.id'))
    portfolio = relationship("Portfolio", backref='allocations')

    instrument_id = Column('instrument', Integer, ForeignKey('instrument.id'))
    instrument = relationship('Instrument')

    percentage = Column('percentage', Float)

    def __repr__(self):
        return "%s-%s" % (self.portfolio.name, self.instrument.name)


engine = create_engine("sqlite:///%s" % DATABASE if DATABASE else "sqlite://")
session_factory = sessionmaker(bind=engine)
finance_db_session = scoped_session(session_factory)
