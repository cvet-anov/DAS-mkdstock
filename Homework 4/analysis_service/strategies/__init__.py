from .base import AnalysisStrategy
from .sma_strategy import SMAStrategy
from .rsi_strategy import RSIStrategy
from .macd_strategy import MACDStrategy
from .bollinger_strategy import BollingerStrategy

class AnalysisFactory:
    @staticmethod
    def create_strategy(strategy_type: str) -> AnalysisStrategy:
        strategies = {
            'sma': SMAStrategy,
            'rsi': RSIStrategy,
            'macd': MACDStrategy,
            'bollinger': BollingerStrategy
        }

        strategy_class = strategies.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"Unknown strategy type: {strategy_type}")

        return strategy_class()