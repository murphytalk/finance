#!/usr/bin/env python
from collections import deque
import unittest
from unittest.case import SkipTest
from unittest.mock import MagicMock, patch
from datetime import timedelta
from finance import app
from finance.api.endpoints.report import Positions
from finance.common.calculate import CalcPosition
from finance.common.dao.impl import ImplDao, Transaction
from finance.common.dao.random import RandomDataDao
from finance.common.dao.utils import DAY1, TODAY, URL
from finance.common.model import Instrument, Position, Quote
from finance.common.utils import epoch2date, get_random_dict_value, get_random_dict_key

YYYY_MM_DD = "%Y-%m-%d"


class TestPosition(unittest.TestCase):
    def test_buy(self):
        p = Position(1, "test")

        data = [
            ("BUY", 100, 10, 0),
            ("BUY", 200, 15, 0),
            ("BUY", 300, 20, 0),
            ("BUY", 400, 30, 0),
        ]

        for trans in data:
            p.transaction(trans[0], trans[1], trans[2], trans[3])

        self.assertAlmostEqual(p.VWAP(), 293.333, 3)
        expected = deque([Position.Unclosed(t[1], t[2], t[3]) for t in data])
        self.assertCountEqual(expected, p.unclosed_positions)

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


class TestCaclPosition(unittest.TestCase):
    def test_one_broker(self):
        dao = ImplDao(None)
        dao.iterate_transaction = MagicMock(return_value=iter([
            Transaction(1, 'I1', 'b1', 'BUY', 1.0, 10, 1.0),
            Transaction(1, 'I1', 'b1', 'BUY', 1.0, 10, 1.0),
            Transaction(2, 'I2', 'b2', 'BUY', 2.0, 10, 1.0),
            Transaction(1, 'I1', 'b1', 'SELL', 2.0, 20, 1.0),
        ]))
        expected = {
            'b1': {1: Position(1, 'I1', 0, 20.0, 3.0, deque())},
            'b2': {2: Position(2, 'I2', 10, -20.0, 1.0, deque([Position.Unclosed(2.0, 10, 1.0)]))}
        }
        pos = CalcPosition(None)
        pos.calc(dao)
        self.assertDictEqual(pos.positions, expected)

    def test_two_brokers(self):
        dao = ImplDao(None)
        dao.iterate_transaction = MagicMock(return_value=iter([
            Transaction(1, 'I1', 'b1', 'BUY', 1.0, 10, 1.0),
            Transaction(1, 'I1', 'b1', 'BUY', 1.0, 10, 1.0),
            Transaction(1, 'I1', 'b1', 'SELL', 2.0, 10, 1.0),

            Transaction(1, 'I1', 'b2', 'BUY', 1.0, 20, 1.0),
            Transaction(2, 'I2', 'b2', 'BUY', 3.0, 10, 1.0),
            Transaction(2, 'I2', 'b2', 'SELL', 2.0, 5, 1.0),
        ]))
        pos = CalcPosition(None)
        pos.calc(dao)
        expected = {
            'b1': {1: Position(1, 'I1', 10.0, 0.0, 3.0, deque([Position.Unclosed(1.0, 10, 1.0)]))},
            'b2': {
                1: Position(1, 'I1', 20.0, -20.0, 1.0, deque([Position.Unclosed(1.0, 20.0, 1.0)])),
                2: Position(2, 'I2', 5.0, -20.0, 2.0, deque([Position.Unclosed(3.0, 5.0, 1.0)]))
            }
        }
        self.assertDictEqual(expected, pos.positions)


class TestReport(unittest.TestCase):
    @patch('finance.common.dao.Dao')
    def test_position_report(self, MockedDao):
        with app.app_context():
            dao = MockedDao.return_value
            dao.get_funds_positions.return_value = iter([
                {'broker': 'b1', 'name': 'f1', 'instrument_id': 10, 'url': 'url1', 'expense_ratio': 1, 'amount': 100, 'price': 110, 'value': 120, 'profit': 130, 'capital': 140, 'date': 0},
                {'broker': 'b1', 'name': 'f2', 'instrument_id': 20, 'url': 'url2', 'expense_ratio': 2, 'amount': 200, 'price': 210, 'value': 220, 'profit': 230, 'capital': 240, 'date': 0},
                {'broker': 'b2', 'name': 'f3', 'instrument_id': 30, 'url': 'url3', 'expense_ratio': 3, 'amount': 300, 'price': 310, 'value': 320, 'profit': 330, 'capital': 340, 'date': 0},
            ])

            dao.get_stock_latest_quotes.return_value = {
                1: Quote(1, 'I1', 110, 0),
                2: Quote(2, 'I2', 120, 0),
                3: Quote(3, 'E1', 130, 0),
                4: Quote(4, 'E2', 140, 0),
            }
            dao.get_instrument_with_xccy_rate.return_value = {
                1: Instrument(1, 'I1', 'Stock', currency='JPY', xccy_rate=1, xccy_rate_date=0),
                2: Instrument(2, 'I2', 'Stock', currency='JPY', xccy_rate=1, xccy_rate_date=0),
                3: Instrument(3, 'E1', 'ETF', currency='JPY', xccy_rate=1, xccy_rate_date=0),
                4: Instrument(4, 'E2', 'ETF', currency='JPY', xccy_rate=1, xccy_rate_date=0),
            }

            def side_effect_iterate_trans(*args, **kwargs):
                return iter([
                    Transaction(1, 'I1', 'b1', 'BUY', 1.0, 10, 1.0),
                    Transaction(1, 'I1', 'b1', 'BUY', 1.0, 10, 1.0),
                    Transaction(1, 'I1', 'b1', 'SELL', 2.0, 10, 1.0),

                    Transaction(1, 'I1', 'b2', 'BUY', 1.0, 20, 1.0),
                    Transaction(2, 'I2', 'b2', 'BUY', 3.0, 10, 1.0),
                    Transaction(2, 'I2', 'b2', 'SELL', 2.0, 5, 1.0),
                ] if args[2] == 'Stock' else [
                    Transaction(3, 'E1', 'b1', 'BUY', 1.0, 10, 1.0),
                    Transaction(4, 'E2', 'b2', 'BUY', 1.0, 10, 1.0),
                ])

            dao.iterate_transaction.side_effect = side_effect_iterate_trans
            dao.get_asset_allocation.return_value = iter([('Stock', 100)])
            dao.get_country_allocation.return_value = iter([('Japan', 100)])
            dao.get_region_allocation.return_value = iter([('Asia', 100)])

            # see Dao's implementation
            MockedDao.singleton = dao
            pos = Positions()
            pos.get()


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
                "Brazil"
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
                    "Broker": 'IB',
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
        self.assertEqual(i["url"], url)


if __name__ == "__main__":
    unittest.main(verbosity=2)
