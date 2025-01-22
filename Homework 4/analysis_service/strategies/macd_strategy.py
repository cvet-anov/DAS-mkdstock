from .base import AnalysisStrategy
import pandas as pd

class MACDStrategy(AnalysisStrategy):
    def analyze(self, data: pd.DataFrame) -> dict:
        try:
            exp1 = data['Last_Price'].ewm(span=12, adjust=False).mean()
            exp2 = data['Last_Price'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal = macd.ewm(span=9, adjust=False).mean()
            histogram = macd - signal

            return {
                'macd': {
                    'macd': float(macd.iloc[-1]) if not pd.isna(macd.iloc[-1]) else None,
                    'signal': float(signal.iloc[-1]) if not pd.isna(signal.iloc[-1]) else None,
                    'histogram': float(histogram.iloc[-1]) if not pd.isna(histogram.iloc[-1]) else None
                }
            }
        except Exception:
            return {'macd': {}}