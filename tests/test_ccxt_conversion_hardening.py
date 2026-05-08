"""Tests for CcxtReadOnlyMarketDataAdapter conversion layer hardening.

Covers: side normalization, CcxtConversionError on malformed fields,
PROHIBITED_CLIENT_METHODS completeness, and __all__ surface.
"""

import sys
import unittest
from decimal import Decimal

from packages.common import MarketDataRequest
from packages.sdk.market_data_adapters.ccxt_readonly import (
    CcxtConversionError,
    CcxtReadOnlyMarketDataAdapter,
    PROHIBITED_CLIENT_METHODS,
    UnsafeCcxtClientError,
)


def _req() -> MarketDataRequest:
    return MarketDataRequest(
        symbol="BTC/USDT", venue="ccxt:fake", asset_class="crypto", instrument_type="spot"
    )


class _BaseClient:
    def fetch_ohlcv(self, symbol: str, limit=None) -> list:
        return []

    def fetch_order_book(self, symbol: str, limit=None) -> dict:
        return {"timestamp": None, "bids": [], "asks": []}


class _TradeClient(_BaseClient):
    def __init__(self, side):
        self._side = side

    def fetch_trades(self, symbol: str, limit=None) -> list:
        return [{"timestamp": 1710000000000, "price": "100", "amount": "1", "side": self._side}]


class _OHLCVClient(_BaseClient):
    def __init__(self, row):
        self._row = row

    def fetch_ohlcv(self, symbol: str, limit=None) -> list:
        return [self._row]

    def fetch_trades(self, symbol: str, limit=None) -> list:
        return []


class SideNormalizationTests(unittest.TestCase):
    """Trade side must be normalized to canonical lowercase or None."""

    def _trades(self, side) -> list:
        return CcxtReadOnlyMarketDataAdapter(_TradeClient(side)).fetch_trades(_req())

    def test_lowercase_buy_preserved(self):
        self.assertEqual(self._trades("buy")[0].side, "buy")

    def test_uppercase_buy_normalized(self):
        self.assertEqual(self._trades("BUY")[0].side, "buy")

    def test_mixed_case_sell_normalized(self):
        self.assertEqual(self._trades("Sell")[0].side, "sell")

    def test_none_side_preserved(self):
        self.assertIsNone(self._trades(None)[0].side)

    def test_unknown_side_normalized_to_none(self):
        self.assertIsNone(self._trades("long")[0].side)

    def test_numeric_side_normalized_to_none(self):
        self.assertIsNone(self._trades(1)[0].side)


class CcxtConversionErrorTests(unittest.TestCase):
    """CcxtConversionError raised on None or invalid numeric fields."""

    def test_none_open_field_raises_conversion_error(self):
        adapter = CcxtReadOnlyMarketDataAdapter(
            _OHLCVClient([1710000000000, None, "110", "90", "105", "1.0"])
        )
        with self.assertRaises(CcxtConversionError):
            adapter.fetch_ohlcv(_req())

    def test_none_high_field_raises_conversion_error(self):
        adapter = CcxtReadOnlyMarketDataAdapter(
            _OHLCVClient([1710000000000, "100", None, "90", "105", "1.0"])
        )
        with self.assertRaises(CcxtConversionError):
            adapter.fetch_ohlcv(_req())

    def test_non_numeric_price_raises_conversion_error(self):
        adapter = CcxtReadOnlyMarketDataAdapter(
            _OHLCVClient([1710000000000, "not-a-number", "110", "90", "105", "1.0"])
        )
        with self.assertRaises(CcxtConversionError):
            adapter.fetch_ohlcv(_req())

    def test_conversion_error_is_value_error(self):
        self.assertTrue(issubclass(CcxtConversionError, ValueError))

    def test_conversion_error_message_includes_field_name(self):
        adapter = CcxtReadOnlyMarketDataAdapter(
            _OHLCVClient([1710000000000, None, "110", "90", "105", "1.0"])
        )
        with self.assertRaises(CcxtConversionError) as ctx:
            adapter.fetch_ohlcv(_req())
        self.assertIn("open", str(ctx.exception))


class ProhibitedClientMethodsTests(unittest.TestCase):
    """PROHIBITED_CLIENT_METHODS must cover all critical execution paths."""

    REQUIRED_METHODS = {
        "create_order",
        "cancel_order",
        "edit_order",
        "withdraw",
        "transfer",
        "set_leverage",
        "private_post_order",
        "private_delete_order",
    }

    def test_all_required_prohibited_methods_present(self):
        self.assertTrue(
            self.REQUIRED_METHODS.issubset(PROHIBITED_CLIENT_METHODS),
            f"missing: {self.REQUIRED_METHODS - PROHIBITED_CLIENT_METHODS}",
        )

    def test_prohibited_methods_is_frozenset(self):
        self.assertIsInstance(PROHIBITED_CLIENT_METHODS, frozenset)

    def test_client_with_any_prohibited_method_is_rejected(self):
        for method in PROHIBITED_CLIENT_METHODS:
            with self.subTest(method=method):
                bad_client = type(
                    f"Unsafe_{method}", (_BaseClient,), {method: lambda self: None}
                )()
                with self.assertRaises(UnsafeCcxtClientError):
                    CcxtReadOnlyMarketDataAdapter(bad_client)


class PublicApiSurfaceTests(unittest.TestCase):
    """Verify __all__ is complete and ccxt is never imported."""

    def test_no_ccxt_import_after_module_load(self):
        self.assertNotIn("ccxt", sys.modules)

    def test_all_exports_importable(self):
        import packages.sdk.market_data_adapters.ccxt_readonly as module
        for name in module.__all__:
            self.assertTrue(hasattr(module, name), f"__all__ entry {name!r} not found")

    def test_ccxt_conversion_error_in_all(self):
        import packages.sdk.market_data_adapters.ccxt_readonly as module
        self.assertIn("CcxtConversionError", module.__all__)


if __name__ == "__main__":
    unittest.main()
