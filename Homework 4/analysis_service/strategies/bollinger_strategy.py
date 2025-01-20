from .base import AnalysisStrategy
import pandas as pd


class BollingerStrategy(AnalysisStrategy):
    def analyze(self, data: pd.DataFrame) -> dict:
        period = 20
        sma = data['Last_Price'].rolling(window=period).mean()
        std = data['Last_Price'].rolling(window=period).std()

        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)

        return {
            'middle': float(sma.iloc[-1]) if not pd.isna(sma.iloc[-1]) else None,
            'upper': float(upper_band.iloc[-1]) if not pd.isna(upper_band.iloc[-1]) else None,
            'lower': float(lower_band.iloc[-1]) if not pd.isna(lower_band.iloc[-1]) else None
        }