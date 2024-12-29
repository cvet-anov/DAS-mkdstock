import pandas as pd
import numpy as np
from typing import Dict, List

class TechnicalAnalysis:
    def __init__(self, df: pd.DataFrame):
        """Initialize with a DataFrame containing stock data."""
        self.df = df.copy()
        if 'Date' in self.df.columns:
            self.df['Date'] = pd.to_datetime(self.df['Date'])
            self.df.set_index('Date', inplace=True)
        else:
            self.df.index = pd.to_datetime(self.df.index)

        self.df = self.df.sort_index()

    def calculate_sma(self, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return self.df['Last_Price'].rolling(window=period).mean()

    def calculate_ema(self, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return self.df['Last_Price'].ewm(span=period, adjust=False).mean()

    def calculate_rsi(self, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index with proper error handling"""
        try:
            delta = self.df['Last_Price'].diff()
            gains = delta.where(delta > 0, 0.0)
            losses = -delta.where(delta < 0, 0.0)

            avg_gains = gains.rolling(window=period).mean()
            avg_losses = losses.rolling(window=period).mean()

            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))

            rsi = rsi.fillna(50)
            return rsi
        except Exception as e:
            print(f"Error calculating RSI: {str(e)}")
            return pd.Series([50] * len(self.df))

    def calculate_macd(self) -> Dict[str, pd.Series]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        exp1 = self.df['Last_Price'].ewm(span=12, adjust=False).mean()
        exp2 = self.df['Last_Price'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        return {'macd': macd, 'signal': signal, 'hist': hist}

    def calculate_bollinger_bands(self, period: int = 20) -> Dict[str, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = self.calculate_sma(period)
        std = self.df['Last_Price'].rolling(window=period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return {'middle': sma, 'upper': upper_band, 'lower': lower_band}

    def calculate_stochastic(self, period: int = 14) -> Dict[str, pd.Series]:
        """Calculate Stochastic Oscillator"""
        low_min = self.df['Low'].rolling(window=period).min()
        high_max = self.df['High'].rolling(window=period).max()
        k = 100 * ((self.df['Last_Price'] - low_min) / (high_max - low_min))
        d = k.rolling(window=3).mean()
        return {'k': k, 'd': d}

    def generate_signals(self) -> Dict[str, List[str]]:
        """Generate trading signals based on technical indicators"""
        signals = {
            'sma': [],
            'ema': [],
            'rsi': [],
            'macd': [],
            'bollinger': []
        }

        sma20 = self.calculate_sma(20)
        sma50 = self.calculate_sma(50)
        signals['sma'] = ['buy' if sma20[i] > sma50[i] else 'sell' for i in range(len(sma20))]

        rsi = self.calculate_rsi()
        signals['rsi'] = ['buy' if r < 30 else 'sell' if r > 70 else 'hold' for r in rsi]

        macd_data = self.calculate_macd()
        signals['macd'] = ['buy' if macd_data['macd'][i] > macd_data['signal'][i]
                           else 'sell' for i in range(len(macd_data['macd']))]

        return signals

    def analyze_all_periods(self) -> Dict:
        """Analyze data for different time periods (1 day, 1 week, 1 month)"""
        try:
            # Create resampled dataframes
            weekly_df = self.df.resample('W').agg({
                'Last_Price': 'last',
                'High': 'max',
                'Low': 'min',
                'Volume': 'sum'
            }).dropna()

            monthly_df = self.df.resample('M').agg({
                'Last_Price': 'last',
                'High': 'max',
                'Low': 'min',
                'Volume': 'sum'
            }).dropna()

            periods = {
                'daily': self.df,
                'weekly': weekly_df,
                'monthly': monthly_df
            }

            analysis = {}
            for period_name, period_data in periods.items():
                temp_analyzer = TechnicalAnalysis(period_data)
                analysis[period_name] = {
                    'sma20': temp_analyzer.calculate_sma(20).iloc[-1],
                    'ema20': temp_analyzer.calculate_ema(20).iloc[-1],
                    'rsi': temp_analyzer.calculate_rsi().iloc[-1],
                    'macd': temp_analyzer.calculate_macd()['macd'].iloc[-1],
                    'bollinger': temp_analyzer.calculate_bollinger_bands()
                }

            return analysis
        except Exception as e:
            print(f"Error in analyze_all_periods: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return {}