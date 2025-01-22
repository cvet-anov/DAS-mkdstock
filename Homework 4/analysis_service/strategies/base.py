from abc import ABC, abstractmethod
import pandas as pd

class AnalysisStrategy(ABC):
    @abstractmethod
    def analyze(self, data: pd.DataFrame) -> dict:
        """
        Analyze the given data and return results
        Args:
            data (pd.DataFrame): DataFrame with columns Date, Last_Price, etc.
        Returns:
            dict: Analysis results
        """
        pass