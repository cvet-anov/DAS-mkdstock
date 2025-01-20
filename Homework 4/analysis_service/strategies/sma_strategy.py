from .base import AnalysisStrategy
import pandas as pd


class SMAStrategy(AnalysisStrategy):
    def analyze(self, data: pd.DataFrame) -> dict:
        sma20 = data['Last_Price'].rolling(window=20).mean()
        sma50 = data['Last_Price'].rolling(window=50).mean()

        return {
            'sma20': float(sma20.iloc[-1]) if not pd.isna(sma20.iloc[-1]) else None,
            'sma50': float(sma50.iloc[-1]) if not pd.isna(sma50.iloc[-1]) else None,
            'signal': 'buy' if sma20.iloc[-1] > sma50.iloc[-1] else 'sell'
        }