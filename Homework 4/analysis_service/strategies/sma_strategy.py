from .base import AnalysisStrategy
import pandas as pd

class SMAStrategy(AnalysisStrategy):
    def analyze(self, data: pd.DataFrame) -> dict:
        try:
            sma20 = data['Last_Price'].rolling(window=20).mean().iloc[-1]
            sma50 = data['Last_Price'].rolling(window=50).mean().iloc[-1]
            ema20 = data['Last_Price'].ewm(span=20, adjust=False).mean().iloc[-1]

            return {
                'sma': {
                    'sma20': float(sma20) if not pd.isna(sma20) else None,
                    'sma50': float(sma50) if not pd.isna(sma50) else None,
                    'ema20': float(ema20) if not pd.isna(ema20) else None
                }
            }
        except Exception:
            return {'sma': {}}