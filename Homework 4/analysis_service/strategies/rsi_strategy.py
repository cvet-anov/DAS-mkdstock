from .base import AnalysisStrategy
import pandas as pd

class RSIStrategy(AnalysisStrategy):
    def analyze(self, data: pd.DataFrame) -> dict:
        try:
            rsi = self._calculate_rsi(data)
            current_rsi = float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None
            return {'rsi': {'rsi': current_rsi}}
        except Exception:
            return {'rsi': {}}

    def _calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        delta = data['Last_Price'].diff()
        gains = delta.where(delta > 0, 0.0)
        losses = -delta.where(delta < 0, 0.0)
        avg_gains = gains.rolling(window=period).mean()
        avg_losses = losses.rolling(window=period).mean()
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)