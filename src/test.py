#!/usr/bin/env python
import unittest
from datetime import timedelta

from finance.common.dao.random import RandomDataDao
from finance.common.dao.utils import *
from finance.common.model import Position
from finance.common.utils import epoch2date, get_random_dict_value, get_random_dict_key

YYYY_MM_DD = "%Y-%m-%d"


class TestPosition(unittest.TestCase):
    def test_buy(self):
        p = Position(1, "test")
        for trans in [
            ("BUY", 100, 10, 0),
            ("BUY", 200, 15, 0),
            ("BUY", 300, 20, 0),
            ("BUY", 400, 30, 0),
        ]:
            p.transaction(trans[0], trans[1], trans[2], trans[3])
        self.assertAlmostEqual(p.VWAP(), 293.333, 3)

    def test_split(self):
        p = Position(1, "test")
        for trans in [
            ("BUY", 100, 10, 0),
            ("BUY", 200, 10, 0),
            ("BUY", 300, 20, 0),
            ("BUY", 400, 30, 0),
            ("SPLIT", 2, 0, 0),
        ]:
            p.transaction(trans[0], trans[1], trans[2], trans[3])
        self.assertEqual(p.VWAP(), 150)

    def test_buy_sell(self):
        p = Position(1, "test")
        for trans in [
            ("BUY", 100, 10, 0),
            ("BUY", 200, 15, 0),
            ("SELL", 150, 20, 0),
            ("BUY", 400, 30, 0),
        ]:
            p.transaction(trans[0], trans[1], trans[2], trans[3])
        self.assertAlmostEqual(p.VWAP(), 371.4286, 4)

    def test_closed_position(self):
        p = Position(1, "test")
        for trans in [
            ("BUY", 100, 10, 0),
            ("BUY", 200, 15, 0),
            ("SELL", 150, 20, 0),
            ("SELL", 150, 5, 0),
        ]:
            p.transaction(trans[0], trans[1], trans[2], trans[3])
        self.assertEqual(p.VWAP(), 0)


class TestDao(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dao = RandomDataDao()

    @staticmethod
    def _raw_queryset_with_id_to_set(qs):
        return frozenset([c for r, c in qs])

    def setUp(self):
        # setup reference data
        self.countries = self._raw_queryset_with_id_to_set(self.dao.get_countries())
        self.country_name_to_id = {n: i for i, n in self.dao.get_countries()}
        self.asset_types = self._raw_queryset_with_id_to_set(self.dao.get_asset_types())
        self.instrument_types = self._raw_queryset_with_id_to_set(
            self.dao.get_instrument_types()
        )
        self.brokers = self.dao.get_broker_mapper()
        self.ccy = self.dao.get_currency_mapper()
        self.instruments = self.dao.populate_from_instruments(None, None)

    def test_reference_data(self):
        self.assertEqual(
            self.countries,
            {
                "Africa Other",
                "Asia Other",
                "Australia",
                "Canada",
                "China",
                "E.Europe Other",
                "Europe placeholder",
                "France",
                "Germany",
                "Hong Kong",
                "India",
                "Japan",
                "Middle East Other",
                "NZ",
                "Other",
                "S.America Other",
                "S.Korea",
                "Singapore",
                "Switzerland",
                "Taiwan",
                "UK",
                "US",
                "W.Europe Other",
                "placeholder",
            },
        )
        self.assertEqual(
            self.asset_types,
            {"Cash", "Gold", "REIT", "Corp Bond", "Government Bond", "Other", "Stock"},
        )
        self.assertEqual(self.brokers, {"ABC": 1, "IB": 3, "XYZ": 2})
        self.assertEqual(
            self.instrument_types, {"ETF", "Funds", "Crypto", "Stock", "Bond"}
        )
        self.assertEqual(
            self.ccy,
            {"AUD": 5, "CNY": 4, "EUR": 3, "HKD": 7, "JPY": 1, "NZD": 6, "USD": 2},
        )

        regions = self.dao.get_country_region_lookup()
        self.assertEqual(regions[self.country_name_to_id["US"]], "N.America")
        self.assertEqual(regions[self.country_name_to_id["UK"]], "W.Europe")
        self.assertEqual(regions[self.country_name_to_id["Japan"]], "Asia")
        self.assertEqual(regions[self.country_name_to_id["China"]], "Asia")
        self.assertEqual(regions[self.country_name_to_id["Canada"]], "N.America")

    def test_instruments(self):
        # all generated instruments
        for iid, instrument in self.instruments.items():
            self.assertIn(instrument.instrument_type.name, self.instrument_types)
            self.assertEqual(instrument.url, URL)

            i = self.dao.get_instruments(instrument.name).__next__()
            self.assertIn(i["currency"], self.ccy)
            self.assertIn(i["broker"], self.brokers)
            self.assertEqual(i["name"], instrument.name)

            for a in self.dao.get_asset_allocation(instrument_name=instrument.name):
                self.assertIn(a[0], self.asset_types)
                self.assertIsInstance(a[1], float)

            for c in self.dao.get_country_allocation(instrument_name=instrument.name):
                self.assertIn(c[0], self.countries)
                self.assertIsInstance(c[1], float)

        for iid, quote in self.dao.get_stock_latest_quotes(TODAY).items():
            self.assertTrue(iid in self.instruments)
            self.assertTrue(epoch2date(TODAY) >= quote.date)
            self.assertTrue(epoch2date(DAY1) <= quote.date)

        for iid, instrument in self.dao.get_instrument_with_xccy_rate(
            epoch2date(TODAY)
        ).items():
            self.assertIn(iid, self.instruments)
            self.assertIn(instrument.instrument_type.name, self.instrument_types)
            self.assertIn(instrument.currency, self.ccy)
            self.assertTrue(instrument.xccy_date <= epoch2date(TODAY))

    def test_funds(self):
        for pos in self.dao.get_funds_positions(TODAY):
            self.assertTrue(pos["instrument_id"] in self.instruments)
            self.assertEqual(
                self.instruments[pos["instrument_id"]].instrument_type.name, "Funds"
            )
            # self.assertTrue(pos['currency'] in self.ccy)
            self.assertIn(pos["broker"], self.brokers)
            self.assertIsInstance(pos["amount"], int)
            self.assertIsInstance(pos["value"], float)
            self.assertIsInstance(pos["price"], float)
            self.assertIsInstance(pos["profit"], float)
            self.assertIsInstance(pos["capital"], float)

    def test_stocks(self):
        stock = get_random_dict_value(
            self.instruments,
            lambda x: True if x.instrument_type.name == "Stock" else False,
        )
        fee = 9.99
        shares = 99
        price = 9.1234
        trans_type = "SELL"
        dt = (epoch2date(TODAY) + timedelta(days=1)).strftime(YYYY_MM_DD)
        self.assertTrue(
            self.dao.update_stock_transaction(
                stock.name,
                {
                    "Price": price,
                    "Type": trans_type,
                    "Date": dt,
                    "Fee": fee,
                    "Shares": shares,
                },
            )
        )
        for trans in self.dao.get_stock_transaction(stock.name):
            self.assertEqual(trans["symbol"], stock.name)
            self.assertIn(trans["type"], {"BUY", "SELL", "SPLIT"})
            self.assertIsInstance(trans["price"], float)
            self.assertIsInstance(trans["fee"], float)
            self.assertIsInstance(trans["shares"], float)
            if trans["date"] == dt:
                # the one just added
                self.assertEqual(trans["fee"], fee)
                self.assertEqual(trans["shares"], shares)
                self.assertEqual(trans["price"], price)
                self.assertEqual(trans["type"], trans_type)


def test_update_instrument(self):
    instrument = get_random_dict_value(
        self.instruments, lambda x: True if x.instrument_type.name == "Funds" else False
    )
    url = "http://my.new.com/url"
    expense = 9.99
    ccy = "CNY"
    broker = get_random_dict_key(self.brokers)

    payload = {"currency": ccy, "broker": broker, "url": url, "expense": expense}

    # update existing
    self.assertTrue(self.dao.update_instrument(instrument.name, payload))
    i = self.dao.get_instruments(instrument.name).__next__()
    self.assertEqual(i["type"], "Funds")
    self.assertEqual(i["currency"], ccy)
    self.assertEqual(i["broker"], broker)
    self.assertEqual(i["url"], url)
    self.assertEqual(i["expense"], expense)

    # update allocations
    # asset allocation
    assets = set(self.asset_types)
    a1 = assets.pop()
    a2 = assets.pop()
    self.assertTrue(
        self.dao.update_instrument_asset_allocations(
            instrument.name,
            {"assets": [{"asset": a1, "ratio": 20}, {"asset": a2, "ratio": 80}]},
        )
    )
    a = {
        t: r for t, r in self.dao.get_asset_allocation(instrument_name=instrument.name)
    }
    self.assertEqual(a[a1], 20)
    self.assertEqual(a[a2], 80)

    # country allocation
    countries = set(self.countries)
    c1 = countries.pop()
    c2 = countries.pop()
    self.assertTrue(
        self.dao.update_instrument_country_allocations(
            instrument.name,
            {"countries": [{"country": c1, "ratio": 20}, {"country": c2, "ratio": 80}]},
        )
    )
    c = {
        t: r
        for t, r in self.dao.get_country_allocation(instrument_name=instrument.name)
    }
    self.assertEqual(c[c1], 20)
    self.assertEqual(c[c2], 80)

    # insert new instrument
    name = instrument.name + ":this is a new instrument"
    # before insert
    self.assertRaises(StopIteration, self.dao.get_instruments(name).__next__)
    # now insert and verify
    payload.pop("expense")
    payload["type"] = "Stock"
    self.assertTrue(self.dao.update_instrument(name, payload))
    i = self.dao.get_instruments(name).__next__()
    self.assertEqual(i["type"], "Stock")
    self.assertEqual(i["currency"], ccy)
    self.assertEqual(i["broker"], broker)
    self.assertEqual(i["url"], url)


if __name__ == "__main__":
    unittest.main(verbosity=2)
