"""
Intelligent Missing Value Handler
Automatically decides the best strategy for handling missing values
"""

import pandas as pd
import numpy as np
from scipy import stats


class MissingValueHandler:
    """Handles missing values with intelligent decision making"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.strategies = {}
        self.missing_info = {}
        
    def analyze_missing_values(self):
        """Analyze missing values in the dataset"""
        missing_counts = self.df.isnull().sum()
        missing_percentages = (missing_counts / len(self.df)) * 100
        
        self.missing_info = {
            'counts': missing_counts[missing_counts > 0],
            'percentages': missing_percentages[missing_percentages > 0]
        }
        
        return self.missing_info
    
    def decide_strategy(self, column):
        """Decide the best strategy for handling missing values in a column"""
        missing_pct = (self.df[column].isnull().sum() / len(self.df)) * 100
        
        # If more than 50% missing, consider dropping
        if missing_pct > 50:
            return 'drop'
        
        # Get column data type
        dtype = self.df[column].dtype
        
        # For numeric columns
        if pd.api.types.is_numeric_dtype(self.df[column]):
            # Check for outliers using IQR
            Q1 = self.df[column].quantile(0.25)
            Q3 = self.df[column].quantile(0.75)
            IQR = Q3 - Q1
            
            # If high variance or outliers, use median
            if self.df[column].std() / self.df[column].mean() > 0.5 or IQR > (Q3 - Q1) * 2:
                return 'median'
            else:
                return 'mean'
        
        # For categorical/object columns
        elif pd.api.types.is_object_dtype(self.df[column]) or pd.api.types.is_categorical_dtype(self.df[column]):
            return 'mode'
        
        # For datetime columns
        elif pd.api.types.is_datetime64_any_dtype(self.df[column]):
            return 'forward_fill'  # Forward fill for time series
        
        # Default to forward fill
        else:
            return 'forward_fill'
    
    def handle_missing_values(self, auto=True):
        """Handle missing values based on intelligent decisions"""
        self.analyze_missing_values()
        
        columns_with_missing = self.missing_info['counts'].index.tolist()
        
        if not columns_with_missing:
            return self.df, self.strategies
        
        for column in columns_with_missing:
            strategy = self.decide_strategy(column)
            self.strategies[column] = strategy
            
            if strategy == 'drop':
                # Drop if more than 50% missing
                self.df = self.df.drop(columns=[column])
                continue
            
            elif strategy == 'mean':
                self.df[column].fillna(self.df[column].mean(), inplace=True)
            
            elif strategy == 'median':
                self.df[column].fillna(self.df[column].median(), inplace=True)
            
            elif strategy == 'mode':
                mode_value = self.df[column].mode()
                if len(mode_value) > 0:
                    self.df[column].fillna(mode_value[0], inplace=True)
                else:
                    # If no mode, use forward fill
                    self.df[column].ffill(inplace=True)
            
            elif strategy == 'forward_fill':
                self.df[column].ffill(inplace=True)
                # If still missing (first values), use backward fill
                self.df[column].bfill(inplace=True)
            
            elif strategy == 'backward_fill':
                self.df[column].bfill(inplace=True)
        
        return self.df, self.strategies
    
    def get_summary(self):
        """Get summary of missing value handling"""
        summary = {
            'total_missing_columns': len(self.missing_info.get('counts', [])),
            'strategies_applied': self.strategies,
            'missing_info': self.missing_info
        }
        return summary

