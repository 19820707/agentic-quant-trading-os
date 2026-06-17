import unittest
from datetime import datetime, timezone
from decimal import Decimal

from packages.domain import Fill, PortfolioSnapshot, SignalSide, Symbol, Venue
from portfolio import (
    PortfolioAccountingError,
    PositionLot,
    SideAwareFill,
    build_portfolio_snapshot,
    position_lots_from_fills,
    reduce_position_lots_from_side_aware_fills,
)


NOW = datetime(2026, 5, 15, 15, 0, tzinfo=timezone.utc)
BTC = Symbol("BTC/USDT")
ETH = Symbol("ETH/USDT")
PAPER = Venue("paper")


class PortfolioAccountingTests(unittest.TestCase):
    def test_position_lots_from_fills_aggregates_weighted_average_and_fees(self):
        fills = (
            Fill(
                fill_id="fill_001",
                order_id="order_001",
                symbol=BTC,
                venue=PAPER,
                filled_at=NOW,
                quantity=Decimal("1"),
                price=Decimal("100"),
                fee=Decimal("0.10"),
            ),
            Fill(
                fill_id="fill_002",
                order_id="order_002",
                symbol=BTC,
                venue=PAPER,
                filled_at=NOW,
                quantity=Decimal("3"),
                price=Decimal("200"),
                fee=Decimal("0.30"),
            ),
        )

        lots = position_lots_from_fills(fills)

        self.assertEqual(len(lots), 1)
        self.assertEqual(lots[0].quantity, Decimal("4"))
        self.assertEqual(lots[0].average_entry_price, Decimal("175"))
        self.assertEqual(lots[0].fees, Decimal("0.40"))

    def test_build_portfolio_snapshot_calculates_exposure_and_pnl(self):
        snapshot = build_portfolio_snapshot(
            portfolio_id="portfolio_local_001",
            timestamp=NOW,
            cash_balances={"USDT": Decimal("1000.00")},
            position_lots=(
                PositionLot(
                    symbol=BTC,
                    venue=PAPER,
                    quantity=Decimal("2"),
                    average_entry_price=Decimal("100"),
                    realized_pnl=Decimal("5"),
                    fees=Decimal("0.25"),
                ),
                PositionLot(
                    symbol=ETH,
                    venue=PAPER,
                    quantity=Decimal("-1"),
                    average_entry_price=Decimal("50"),
                    realized_pnl=Decimal("2"),
                    fees=Decimal("0.10"),
                ),
            ),
            mark_prices={
                ("BTC/USDT", "paper"): Decimal("120"),
                ("ETH/USDT", "paper"): Decimal("40"),
            },
        )

        self.assertIsInstance(snapshot, PortfolioSnapshot)
        self.assertEqual(snapshot.exposure.by_symbol["BTC/USDT"], Decimal("240"))
        self.assertEqual(snapshot.exposure.by_symbol["ETH/USDT"], Decimal("-40"))
        self.assertEqual(snapshot.exposure.gross_exposure, Decimal("280"))
        self.assertEqual(snapshot.exposure.net_exposure, Decimal("200"))
        self.assertEqual(snapshot.pnl.realized, Decimal("7"))
        self.assertEqual(snapshot.pnl.unrealized, Decimal("50"))
        self.assertEqual(snapshot.pnl.fees, Decimal("0.35"))
        self.assertEqual(snapshot.pnl.total, Decimal("56.65"))

    def test_side_aware_reducer_handles_long_open_and_partial_close(self):
        lots = reduce_position_lots_from_side_aware_fills(
            (
                self._side_fill("fill_buy_001", SignalSide.BUY, Decimal("10"), Decimal("100")),
                self._side_fill("fill_sell_001", SignalSide.SELL, Decimal("4"), Decimal("120")),
            )
        )

        self.assertEqual(len(lots), 1)
        self.assertEqual(lots[0].quantity, Decimal("6"))
        self.assertEqual(lots[0].average_entry_price, Decimal("100"))
        self.assertEqual(lots[0].realized_pnl, Decimal("80"))

    def test_side_aware_reducer_handles_full_close_to_flat(self):
        lots = reduce_position_lots_from_side_aware_fills(
            (
                self._side_fill("fill_buy_001", SignalSide.BUY, Decimal("2"), Decimal("50")),
                self._side_fill("fill_sell_001", SignalSide.SELL, Decimal("2"), Decimal("45")),
            )
        )

        self.assertEqual(lots[0].quantity, Decimal("0"))
        self.assertEqual(lots[0].average_entry_price, Decimal("0"))
        self.assertEqual(lots[0].realized_pnl, Decimal("-10"))

    def test_side_aware_reducer_handles_flip_from_long_to_short(self):
        lots = reduce_position_lots_from_side_aware_fills(
            (
                self._side_fill("fill_buy_001", SignalSide.BUY, Decimal("2"), Decimal("100")),
                self._side_fill("fill_sell_001", SignalSide.SELL, Decimal("5"), Decimal("110")),
            )
        )

        self.assertEqual(lots[0].quantity, Decimal("-3"))
        self.assertEqual(lots[0].average_entry_price, Decimal("110"))
        self.assertEqual(lots[0].realized_pnl, Decimal("20"))

    def test_side_aware_reducer_handles_short_profit(self):
        lots = reduce_position_lots_from_side_aware_fills(
            (
                self._side_fill("fill_short_001", SignalSide.SELL, Decimal("3"), Decimal("90")),
                self._side_fill("fill_cover_001", SignalSide.BUY, Decimal("1"), Decimal("80")),
            )
        )

        self.assertEqual(lots[0].quantity, Decimal("-2"))
        self.assertEqual(lots[0].average_entry_price, Decimal("90"))
        self.assertEqual(lots[0].realized_pnl, Decimal("10"))

    def test_side_aware_reducer_feeds_snapshot_with_signed_exposure(self):
        lots = reduce_position_lots_from_side_aware_fills(
            (
                self._side_fill("fill_short_001", SignalSide.SELL, Decimal("3"), Decimal("90"), fee=Decimal("0.15")),
                self._side_fill("fill_cover_001", SignalSide.BUY, Decimal("1"), Decimal("80"), fee=Decimal("0.05")),
            )
        )

        snapshot = build_portfolio_snapshot(
            portfolio_id="portfolio_side_aware",
            timestamp=NOW,
            cash_balances={"USDT": Decimal("500")},
            position_lots=lots,
            mark_prices={("BTC/USDT", "paper"): Decimal("70")},
        )

        self.assertEqual(snapshot.positions[0].quantity, Decimal("-2"))
        self.assertEqual(snapshot.exposure.net_exposure, Decimal("-140"))
        self.assertEqual(snapshot.exposure.gross_exposure, Decimal("140"))
        self.assertEqual(snapshot.pnl.realized, Decimal("10"))
        self.assertEqual(snapshot.pnl.unrealized, Decimal("40"))
        self.assertEqual(snapshot.pnl.fees, Decimal("0.20"))
        self.assertEqual(snapshot.pnl.total, Decimal("49.80"))

    def test_side_aware_fill_rejects_hold_side(self):
        with self.assertRaises(PortfolioAccountingError):
            self._side_fill("fill_hold_001", SignalSide.HOLD, Decimal("1"), Decimal("100"))

    def test_snapshot_serialization_roundtrip_preserves_positions(self):
        snapshot = build_portfolio_snapshot(
            portfolio_id="portfolio_roundtrip",
            timestamp=NOW,
            cash_balances={"USDT": Decimal("1000.00")},
            position_lots=(
                PositionLot(
                    symbol=BTC,
                    venue=PAPER,
                    quantity=Decimal("1"),
                    average_entry_price=Decimal("100"),
                ),
            ),
            mark_prices={("BTC/USDT", "paper"): Decimal("110")},
        )

        restored = PortfolioSnapshot.from_dict(snapshot.to_dict())

        self.assertEqual(restored.to_dict(), snapshot.to_dict())
        self.assertEqual(restored.positions[0].unrealized_pnl, Decimal("10"))

    def test_missing_mark_price_fails_closed(self):
        with self.assertRaises(PortfolioAccountingError):
            build_portfolio_snapshot(
                portfolio_id="portfolio_missing_mark",
                timestamp=NOW,
                cash_balances={},
                position_lots=(
                    PositionLot(
                        symbol=BTC,
                        venue=PAPER,
                        quantity=Decimal("1"),
                        average_entry_price=Decimal("100"),
                    ),
                ),
                mark_prices={},
            )

    def test_invalid_mark_price_fails_closed(self):
        with self.assertRaises(PortfolioAccountingError):
            build_portfolio_snapshot(
                portfolio_id="portfolio_bad_mark",
                timestamp=NOW,
                cash_balances={},
                position_lots=(
                    PositionLot(
                        symbol=BTC,
                        venue=PAPER,
                        quantity=Decimal("1"),
                        average_entry_price=Decimal("100"),
                    ),
                ),
                mark_prices={("BTC/USDT", "paper"): Decimal("0")},
            )

    def test_calculator_exposes_no_broker_or_execution_methods(self):
        import portfolio.accounting as accounting

        forbidden_names = {
            "buy",
            "sell",
            "order",
            "submit_order",
            "cancel_order",
            "edit_order",
            "withdraw",
            "transfer",
            "execute",
            "connect",
        }

        self.assertTrue(forbidden_names.isdisjoint(dir(accounting)))

    def _side_fill(
        self,
        fill_id: str,
        side: SignalSide,
        quantity: Decimal,
        price: Decimal,
        *,
        fee: Decimal = Decimal("0"),
    ) -> SideAwareFill:
        return SideAwareFill(
            fill_id=fill_id,
            order_id=f"order_{fill_id}",
            symbol=BTC,
            venue=PAPER,
            side=side,
            filled_at=NOW,
            quantity=quantity,
            price=price,
            fee=fee,
        )


if __name__ == "__main__":
    unittest.main()
