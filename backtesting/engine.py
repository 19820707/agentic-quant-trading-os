from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

from market_data.interfaces import MarketDataEvent
from packages.domain import (
    Balance,
    CorrelationId,
    ExposureSnapshot,
    OHLCVCandle,
    OrderIntent,
    OrderStatus,
    OrderType,
    PnL,
    PortfolioSnapshot,
    RiskCheckRequest,
    RiskCheckResult,
    RiskDecision,
    Signal,
    SignalSide,
    TimeInForce,
)
from packages.domain.base import deterministic_id, require_aware_datetime, require_non_empty, require_non_negative
from paper_trading import PaperRuntimeConfig, PaperTradingError, PaperTradeResult, simulate_paper_trade
from risk.evaluator import PriceReference, RiskEvaluation, RiskLimits, RiskRuntimeState, evaluate_risk
from strategies import Strategy, StrategyRuntimeContext


class BacktestError(ValueError):
    """Raised when a local backtest cannot proceed safely."""


@dataclass(frozen=True)
class BacktestConfig:
    backtest_id: str
    portfolio_id: str
    starting_cash: Decimal
    order_quantity: Decimal
    paper_runtime_enabled: bool = False
    live_trading_enabled: bool = False
    network_allowed: bool = False
    credentials_allowed: bool = False
    allow_order_intent_creation: bool = False
    allow_paper_fills: bool = False
    stale_price_after: timedelta = timedelta(minutes=5)

    def __post_init__(self) -> None:
        require_non_empty(self.backtest_id, "backtest_id")
        require_non_empty(self.portfolio_id, "portfolio_id")
        require_non_negative(self.starting_cash, "starting_cash")
        if self.order_quantity <= Decimal("0"):
            raise BacktestError("order_quantity must be positive")
        if self.live_trading_enabled:
            raise BacktestError("live trading must remain disabled for backtests")
        if self.network_allowed:
            raise BacktestError("backtests must not allow network access")
        if self.credentials_allowed:
            raise BacktestError("backtests must not allow credentials")
        if self.allow_paper_fills and not self.paper_runtime_enabled:
            raise BacktestError("paper fills require paper_runtime_enabled")
        if self.stale_price_after.total_seconds() <= 0:
            raise BacktestError("stale_price_after must be positive")


@dataclass(frozen=True)
class BacktestMetrics:
    events_seen: int
    candles_seen: int
    signals_emitted: int
    order_intents_created: int
    risk_checks: int
    rejected_risk_checks: int
    review_risk_checks: int
    approved_risk_checks: int
    paper_orders: int
    paper_fills: int
    final_equity: Decimal
    total_pnl: Decimal
    max_drawdown: Decimal


@dataclass(frozen=True)
class BacktestResult:
    backtest_id: str
    started_at: datetime
    finished_at: datetime
    metrics: BacktestMetrics
    signals: tuple[Signal, ...]
    order_intents: tuple[OrderIntent, ...]
    risk_results: tuple[RiskCheckResult, ...]
    paper_results: tuple[PaperTradeResult, ...]
    warnings: tuple[str, ...] = ()
    runtime_mode: str = "local_research_only"
    live_trading_used: bool = False
    network_used: bool = False
    credentials_used: bool = False
    production_approved: bool = False

    def __post_init__(self) -> None:
        require_non_empty(self.backtest_id, "backtest_id")
        require_aware_datetime(self.started_at, "started_at")
        require_aware_datetime(self.finished_at, "finished_at")
        if self.runtime_mode != "local_research_only":
            raise BacktestError("backtest result must remain local_research_only")
        if self.live_trading_used or self.network_used or self.credentials_used or self.production_approved:
            raise BacktestError("backtest result cannot imply live, network, credential or production approval")


@dataclass
class _BacktestState:
    cash: Decimal
    realized_pnl: Decimal = Decimal("0")
    fees: Decimal = Decimal("0")
    equity_curve: list[Decimal] = field(default_factory=list)


def run_event_driven_backtest(
    *,
    config: BacktestConfig,
    strategy: Strategy,
    events: tuple[MarketDataEvent, ...],
    risk_limits: RiskLimits,
    risk_runtime: RiskRuntimeState | None = None,
    started_at: datetime,
    correlation_id: CorrelationId,
) -> BacktestResult:
    """Run a deterministic local event-driven research backtest.

    The engine does not load external datasets, call brokers, call exchanges,
    approve live trading, train models, or read credentials.
    """

    require_aware_datetime(started_at, "started_at")
    state = _BacktestState(cash=config.starting_cash)
    signals: list[Signal] = []
    intents: list[OrderIntent] = []
    risk_results: list[RiskCheckResult] = []
    paper_results: list[PaperTradeResult] = []
    warnings: list[str] = []
    candles_seen = 0

    for index, event in enumerate(events):
        if not isinstance(event, OHLCVCandle):
            warnings.append(f"ignored_non_candle_event:{type(event).__name__}")
            continue

        candles_seen += 1
        state.equity_curve.append(state.cash)
        context = StrategyRuntimeContext(
            correlation_id=correlation_id.value,
            generated_at=event.timestamp,
        )
        output = strategy.on_market_data(event, context)
        signals.extend(output.signals)

        for signal in output.signals:
            if signal.side is SignalSide.HOLD:
                continue
            if not config.allow_order_intent_creation:
                warnings.append(f"order_intent_creation_blocked:{signal.signal_id}")
                continue

            intent = OrderIntent.from_signal(
                signal,
                quantity=config.order_quantity,
                order_type=OrderType.MARKET,
                created_at=event.timestamp,
                time_in_force=TimeInForce.GTC,
            )
            intents.append(intent)

            risk_result = _evaluate_intent_risk(
                config=config,
                intent=intent,
                candle=event,
                risk_limits=risk_limits,
                risk_runtime=risk_runtime or RiskRuntimeState(kill_switch_active=True, peak_equity=config.starting_cash),
                cash=state.cash,
                evaluated_at=event.timestamp,
                sequence=index,
            )
            risk_results.append(risk_result)

            if not config.allow_paper_fills:
                warnings.append(f"paper_fill_blocked:{intent.order_intent_id}")
                continue

            try:
                paper_result = simulate_paper_trade(
                    intent=intent,
                    risk_result=risk_result,
                    price_reference=_price_reference_from_candle(event),
                    config=PaperRuntimeConfig(paper_runtime_enabled=True),
                    evaluated_at=event.timestamp,
                    correlation_id=correlation_id,
                )
            except PaperTradingError as exc:
                warnings.append(f"paper_fill_rejected:{intent.order_intent_id}:{exc}")
                continue

            paper_results.append(paper_result)
            state = _apply_paper_result_to_cash(state, paper_result)

    finished_at = _finished_at(started_at, events)
    final_equity = state.cash
    metrics = BacktestMetrics(
        events_seen=len(events),
        candles_seen=candles_seen,
        signals_emitted=len(signals),
        order_intents_created=len(intents),
        risk_checks=len(risk_results),
        rejected_risk_checks=sum(1 for result in risk_results if result.decision is RiskDecision.REJECT),
        review_risk_checks=sum(1 for result in risk_results if result.decision is RiskDecision.REVIEW),
        approved_risk_checks=sum(1 for result in risk_results if result.decision is RiskDecision.APPROVE),
        paper_orders=sum(1 for result in paper_results if result.order.status in {OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED}),
        paper_fills=sum(len(result.fills) for result in paper_results),
        final_equity=final_equity,
        total_pnl=final_equity - config.starting_cash,
        max_drawdown=_max_drawdown(tuple(state.equity_curve + [final_equity])),
    )
    return BacktestResult(
        backtest_id=config.backtest_id,
        started_at=started_at,
        finished_at=finished_at,
        metrics=metrics,
        signals=tuple(signals),
        order_intents=tuple(intents),
        risk_results=tuple(risk_results),
        paper_results=tuple(paper_results),
        warnings=tuple(warnings),
    )


def _evaluate_intent_risk(
    *,
    config: BacktestConfig,
    intent: OrderIntent,
    candle: OHLCVCandle,
    risk_limits: RiskLimits,
    risk_runtime: RiskRuntimeState,
    cash: Decimal,
    evaluated_at: datetime,
    sequence: int,
) -> RiskCheckResult:
    request = RiskCheckRequest(
        risk_check_request_id=deterministic_id("bt_risk_request", config.backtest_id, intent.order_intent_id, sequence),
        order_intent=intent,
        portfolio_id=config.portfolio_id,
        requested_at=evaluated_at,
    )
    portfolio = PortfolioSnapshot(
        portfolio_id=config.portfolio_id,
        timestamp=evaluated_at,
        balances=(Balance(asset="USDT", total=cash, available=cash, locked=Decimal("0")),),
        positions=(),
        exposure=ExposureSnapshot(gross_exposure=Decimal("0"), net_exposure=Decimal("0"), by_symbol={}, by_venue={}),
        pnl=PnL(realized=Decimal("0"), unrealized=Decimal("0"), fees=Decimal("0")),
    )
    return evaluate_risk(
        RiskEvaluation(
            request=request,
            portfolio=portfolio,
            limits=risk_limits,
            runtime=risk_runtime,
            price_reference=_price_reference_from_candle(candle),
            evaluated_at=evaluated_at,
        )
    )


def _price_reference_from_candle(candle: OHLCVCandle) -> PriceReference:
    return PriceReference(
        symbol=candle.symbol,
        venue=candle.venue,
        price=candle.close,
        observed_at=candle.timestamp,
        liquidity_notional=candle.close * candle.volume,
    )


def _apply_paper_result_to_cash(state: _BacktestState, result: PaperTradeResult) -> _BacktestState:
    cash = state.cash
    fees = state.fees
    for fill in result.fills:
        notional = fill.quantity * fill.price
        if result.order.side is SignalSide.BUY:
            cash -= notional + fill.fee
        elif result.order.side is SignalSide.SELL:
            cash += notional - fill.fee
        fees += fill.fee
    return _BacktestState(cash=cash, realized_pnl=state.realized_pnl, fees=fees, equity_curve=list(state.equity_curve))


def _finished_at(started_at: datetime, events: tuple[MarketDataEvent, ...]) -> datetime:
    candle_times = [event.timestamp for event in events if isinstance(event, OHLCVCandle)]
    return max(candle_times) if candle_times else started_at


def _max_drawdown(equity_curve: tuple[Decimal, ...]) -> Decimal:
    if not equity_curve:
        return Decimal("0")
    peak = equity_curve[0]
    max_drawdown = Decimal("0")
    for equity in equity_curve:
        if equity > peak:
            peak = equity
        drawdown = peak - equity
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    return max_drawdown
