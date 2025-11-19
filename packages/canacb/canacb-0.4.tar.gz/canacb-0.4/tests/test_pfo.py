#!/usr/bin/env python3
"""
Unit test framework for portfolio module
"""

import unittest

from src.canacb.pfo import PortfolioManager, Portfolio, Holding


class TestManager(unittest.TestCase):
    """ Portfolio manager unit tests """

    def test_bad_additions(self):
        """ Test addition of a bad portfolio """
        pm = PortfolioManager()

        with self.assertRaises(TypeError):
            pm['x'] = 14
        with self.assertRaises(TypeError):
            pm['x'] = "14"
        with self.assertRaises(TypeError):
            pm['x'] = {"transactions": []}
        with self.assertRaises(ValueError):
            pm[None] = Portfolio()
        with self.assertRaises(ValueError):
            pm[""] = Portfolio()
        with self.assertRaises(ValueError):
            pm["       "] = Portfolio()
        pm["x"] = Portfolio()
        with self.assertRaises(KeyError):
            pm["x"] = Portfolio()

    def test_deletions(self):
        """ Test deletion of a portfolio """
        pm = PortfolioManager()
        pm["x"] = Portfolio()
        with self.assertRaises(TypeError):
            del pm["x"]

    def test_additions(self):
        """ Test addition of an ok portfolio """
        pm = PortfolioManager()
        pm["x"] = Portfolio()
        pm["X"] = Portfolio()

    def test_dirt(self):
        pm = PortfolioManager()
        self.assertFalse(pm.is_dirty())
        pm["x"] = Portfolio()
        self.assertTrue(pm.is_dirty())
        pm.mark_clean()
        self.assertFalse(pm.is_dirty())

    def test_names(self):
        pm = PortfolioManager()
        self.assertEqual(pm.pfo_names, [])
        pm["x"] = Portfolio()
        pm["y"] = Portfolio()
        pm["r"] = Portfolio()
        self.assertEqual(pm.pfo_names, ["r", "x", "y"])


class TestPortfolio(unittest.TestCase):
    """ Portfolio unit tests """

    def test_creation(self):
        """ Test creation of a portfolio """
        for bad_arg in (14, 14.0, [], tuple(), set()):
            with self.assertRaises(TypeError):
                pfo = Portfolio(bad_arg)
        pfo = Portfolio()
        self.assertTrue(pfo.is_dirty())
        pfo.mark_clean()
        self.assertFalse(pfo.is_dirty())

    def test_new_holding(self):
        """ Test addition of a holding to a portfolio """
        pfo = Portfolio()
        self.assertEqual(pfo.holding_names, [])
        for bad_symbol in (14, 14.0, None, "", "    "):
            with self.assertRaises(ValueError):
                pfo.add_holding(bad_symbol)
        pfo.add_holding("x")
        with self.assertRaises(KeyError):
            pfo.add_holding("x")
        with self.assertRaises(KeyError):
            pfo.add_holding("x")
        with self.assertRaises(KeyError):
            pfo.add_holding("  x     ")
        self.assertEqual(pfo.holding_names, ["x"])
        pfo.add_holding("w")
        self.assertEqual(pfo.holding_names, ["w", "x"])

    def test_symbol_change(self):
        """ Test change of symbol """
        pfo = Portfolio()
        pfo.add_holding("y")
        pfo.add_holding("X")
        self.assertEqual(pfo.holding_names, ["X", "y"])
        with self.assertRaises(KeyError):
            pfo.change_symbol("z", "a")
        with self.assertRaises(KeyError):
            pfo.change_symbol("y", "x")

    def test_transactions(self):
        """ Test transaction forwarding """
        pfo = Portfolio()
        pfo.add_holding("X")
        pfo.mark_clean()
        pfo.buy("X", "2016-07-14", 100, 20, 4, None, None)
        self.assertTrue(pfo.is_dirty())
        pfo.sell("X", "2018-09-22", 20, 25, 4.95, None, None)
        pfo.split("X", "2017-04-06", 5, 4)
        pfo.adjust("X", "2019-03-31", -17.44, 1.0465, "RoC")
        self.assertTrue(pfo.is_dirty())

        # Following breaks encapsulation
        self.assertEqual(pfo._holdings["X"].total_shares("2016-12-31"), 100.0)
        self.assertEqual(pfo._holdings["X"].total_cost("2016-12-31"), 2004.0)
        self.assertEqual(pfo._holdings["X"].total_shares("2017-12-31"), 125.0)
        self.assertEqual(pfo._holdings["X"].total_cost("2017-12-31"), 2004.0)
        self.assertEqual(pfo._holdings["X"].total_shares("2018-12-31"), 105.0)
        self.assertAlmostEqual(pfo._holdings["X"].total_cost("2018-12-31"), 1683.36)
        self.assertEqual(pfo._holdings["X"].total_shares("2019-12-31"), 105.0)
        self.assertAlmostEqual(pfo._holdings["X"].total_cost("2019-12-31"), 1665.11,
            places=2)


# In case of direct CLI invocation.
if __name__ == "__main__":
    unittest.main()
