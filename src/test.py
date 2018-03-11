#!/usr/bin/env python3
import unittest
from finance.common.model import Position


class TestPosition(unittest.TestCase):
    def test_buy(self):
        p = Position(1, 'test')
        for trans in [
            ('BUY', 100, 10, 0),
            ('BUY', 200, 15, 0),
            ('BUY', 300, 20, 0),
            ('BUY', 400, 30, 0)]:
            p.transaction(trans[0], trans[1], trans[2], trans[3])
        self.assertAlmostEqual(p.VWAP(), 293.333, 3)

    def test_split(self):
        p = Position(1, 'test')
        for trans in [
            ('BUY', 100, 10, 0),
            ('BUY', 200, 10, 0),
            ('BUY', 300, 20, 0),
            ('BUY', 400, 30, 0),
            ('SPLIT', 2, 0, 0)]:
            p.transaction(trans[0], trans[1], trans[2], trans[3])
        self.assertEqual(p.VWAP(), 150)

    def test_buy_sell(self):
        p = Position(1, 'test')
        for trans in [
            ('BUY', 100, 10, 0),
            ('BUY', 200, 15, 0),
            ('SELL', 150, 20, 0),
            ('BUY', 400, 30, 0)]:
            p.transaction(trans[0], trans[1], trans[2], trans[3])
        self.assertAlmostEqual(p.VWAP(), 371.4286, 4)


if __name__ == '__main__':
    unittest.main()