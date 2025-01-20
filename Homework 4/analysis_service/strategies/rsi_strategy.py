from .base import AnalysisStrategy
import pandas as pd


class RSIStrategy(AnalysisStrategy):
    def analyze(self, data: pd.DataFrame) -> dict:
        rsi = self._calculate_rsi(data)
        current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else 50

        return {
            'rsi': current_rsi,
            'signal': 'buy' if current_rsi < 30 else 'sell' if current_rsi > 70 else 'hold'
        }

    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        delta = data['Last_Price'].diff()
        gains = delta.where(delta > 0, 0.0)
        losses = -delta.where(delta < 0, 0.0)

        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()

        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)