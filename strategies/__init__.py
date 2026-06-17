"""Strategy boundary placeholders.

No executable strategy runtime is implemented here yet.
"""
from .base import (
    BaseResearchStrategy,
    PROHIBITED_STRATEGY_METHOD_NAMES,
    Strategy,
    StrategyCapabilityProfile,
    StrategyConfig,
    StrategyError,
    StrategyMode,
    StrategyOutput,
    StrategyRuntimeContext,
    validate_strategy_surface,
)
from .allocator import (
    AllocatedSignalCandidate,
    StrategyPortfolioAllocationPolicy,
    StrategyPortfolioAllocator,
    StrategySignalWeight,
    validate_allocator_surface,
)
from .examples import (
    GridResearchParameters,
    GridResearchStrategy,
    InventoryAwareMarketMakingStrategy,
    InventoryMarketMakingParameters,
    MeanReversionParameters,
    MeanReversionStrategy,
    MovingAverageCrossoverParameters,
    MovingAverageCrossoverStrategy,
    VolatilityBreakoutParameters,
    VolatilityBreakoutStrategy,
)

__all__ = [
    "BaseResearchStrategy",
    "AllocatedSignalCandidate",
    "GridResearchParameters",
    "GridResearchStrategy",
    "InventoryAwareMarketMakingStrategy",
    "InventoryMarketMakingParameters",
    "MeanReversionParameters",
    "MeanReversionStrategy",
    "MovingAverageCrossoverParameters",
    "MovingAverageCrossoverStrategy",
    "PROHIBITED_STRATEGY_METHOD_NAMES",
    "Strategy",
    "StrategyCapabilityProfile",
    "StrategyConfig",
    "StrategyError",
    "StrategyMode",
    "StrategyPortfolioAllocationPolicy",
    "StrategyPortfolioAllocator",
    "StrategySignalWeight",
    "StrategyOutput",
    "StrategyRuntimeContext",
    "VolatilityBreakoutParameters",
    "VolatilityBreakoutStrategy",
    "validate_allocator_surface",
    "validate_strategy_surface",
]
