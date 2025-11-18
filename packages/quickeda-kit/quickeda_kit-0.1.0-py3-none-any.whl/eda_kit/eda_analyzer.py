"""
EDA Analyzer - Performs comprehensive exploratory data analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)


class EDAAnalyzer:
    """Performs comprehensive EDA on the dataset"""
    
    def __init__(self, df):
        self.df = df.copy()
        self.numeric_columns = self.df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_columns = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        self.datetime_columns = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        self.results = {}
        
    def get_basic_info(self):
        """Get basic information about the dataset"""
        info = {
            'shape': self.df.shape,
            'columns': self.df.columns.tolist(),
            'dtypes': self.df.dtypes.to_dict(),
            'memory_usage': self.df.memory_usage(deep=True).sum() / 1024**2,  # MB
            'numeric_columns': self.numeric_columns,
            'categorical_columns': self.categorical_columns,
            'datetime_columns': self.datetime_columns,
        }
        self.results['basic_info'] = info
        return info
    
    def get_descriptive_stats(self):
        """Get descriptive statistics"""
        stats = {
            'numeric': self.df[self.numeric_columns].describe().to_dict() if self.numeric_columns else {},
            'categorical': self.df[self.categorical_columns].describe(include=['object']).to_dict() if self.categorical_columns else {},
        }
        self.results['descriptive_stats'] = stats
        return stats
    
    def detect_outliers(self, column, method='iqr'):
        """Detect outliers in a numeric column"""
        if column not in self.numeric_columns:
            return []
        
        if method == 'iqr':
            Q1 = self.df[column].quantile(0.25)
            Q3 = self.df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = self.df[(self.df[column] < lower_bound) | (self.df[column] > upper_bound)][column]
            return outliers.tolist()
        
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(self.df[column].dropna()))
            outliers = self.df[z_scores > 3][column]
            return outliers.tolist()
        
        return []
    
    def analyze_outliers(self):
        """Analyze outliers for all numeric columns"""
        outlier_analysis = {}
        for col in self.numeric_columns:
            outliers = self.detect_outliers(col)
            outlier_analysis[col] = {
                'count': len(outliers),
                'percentage': (len(outliers) / len(self.df)) * 100,
                'outliers': outliers[:10]  # First 10 outliers
            }
        self.results['outliers'] = outlier_analysis
        return outlier_analysis
    
    def calculate_correlations(self):
        """Calculate correlation matrix for numeric columns"""
        if len(self.numeric_columns) < 2:
            return {}
        
        corr_matrix = self.df[self.numeric_columns].corr()
        
        # Find highly correlated pairs
        high_corr_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:
                    high_corr_pairs.append({
                        'column1': corr_matrix.columns[i],
                        'column2': corr_matrix.columns[j],
                        'correlation': corr_value
                    })
        
        self.results['correlations'] = {
            'matrix': corr_matrix.to_dict(),
            'high_correlation_pairs': high_corr_pairs
        }
        return self.results['correlations']
    
    def analyze_distributions(self):
        """Analyze distributions of numeric columns"""
        distributions = {}
        for col in self.numeric_columns:
            data = self.df[col].dropna()
            if len(data) > 0:
                # Normality test
                if len(data) >= 8:  # Minimum sample size for Shapiro-Wilk
                    try:
                        stat, p_value = stats.shapiro(data[:5000])  # Limit for performance
                        is_normal = p_value > 0.05
                    except:
                        is_normal = None
                else:
                    is_normal = None
                
                distributions[col] = {
                    'mean': data.mean(),
                    'median': data.median(),
                    'std': data.std(),
                    'skewness': data.skew(),
                    'kurtosis': data.kurtosis(),
                    'is_normal': is_normal,
                    'min': data.min(),
                    'max': data.max(),
                }
        
        self.results['distributions'] = distributions
        return distributions
    
    def analyze_categorical(self):
        """Analyze categorical columns"""
        categorical_analysis = {}
        for col in self.categorical_columns:
            value_counts = self.df[col].value_counts()
            categorical_analysis[col] = {
                'unique_count': self.df[col].nunique(),
                'most_frequent': value_counts.index[0] if len(value_counts) > 0 else None,
                'most_frequent_count': value_counts.iloc[0] if len(value_counts) > 0 else 0,
                'value_counts': value_counts.head(10).to_dict(),
            }
        
        self.results['categorical'] = categorical_analysis
        return categorical_analysis
    
    def generate_visualizations(self, save_path=None):
        """Generate visualizations for the dataset"""
        viz_paths = []
        
        # 1. Distribution plots for numeric columns
        if self.numeric_columns:
            n_cols = min(3, len(self.numeric_columns))
            n_rows = (len(self.numeric_columns) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
            axes = axes.flatten() if n_rows > 1 else [axes] if n_cols == 1 else axes
            
            for idx, col in enumerate(self.numeric_columns[:n_rows*n_cols]):
                self.df[col].hist(bins=30, ax=axes[idx])
                axes[idx].set_title(f'Distribution of {col}')
                axes[idx].set_xlabel(col)
                axes[idx].set_ylabel('Frequency')
            
            # Hide extra subplots
            for idx in range(len(self.numeric_columns), len(axes)):
                axes[idx].axis('off')
            
            plt.tight_layout()
            if save_path:
                path = f"{save_path}/distributions.png"
                plt.savefig(path, dpi=150, bbox_inches='tight')
                viz_paths.append(path)
            plt.close()
        
        # 2. Correlation heatmap
        if len(self.numeric_columns) >= 2:
            plt.figure(figsize=(12, 10))
            corr_matrix = self.df[self.numeric_columns].corr()
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0)
            plt.title('Correlation Heatmap')
            plt.tight_layout()
            if save_path:
                path = f"{save_path}/correlation_heatmap.png"
                plt.savefig(path, dpi=150, bbox_inches='tight')
                viz_paths.append(path)
            plt.close()
        
        # 3. Box plots for numeric columns (outlier detection)
        if self.numeric_columns:
            n_cols = min(3, len(self.numeric_columns))
            n_rows = (len(self.numeric_columns) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
            axes = axes.flatten() if n_rows > 1 else [axes] if n_cols == 1 else axes
            
            for idx, col in enumerate(self.numeric_columns[:n_rows*n_cols]):
                self.df.boxplot(column=col, ax=axes[idx])
                axes[idx].set_title(f'Box Plot of {col}')
            
            for idx in range(len(self.numeric_columns), len(axes)):
                axes[idx].axis('off')
            
            plt.tight_layout()
            if save_path:
                path = f"{save_path}/boxplots.png"
                plt.savefig(path, dpi=150, bbox_inches='tight')
                viz_paths.append(path)
            plt.close()
        
        # 4. Categorical value counts
        if self.categorical_columns:
            n_cols = min(2, len(self.categorical_columns))
            n_rows = (len(self.categorical_columns) + n_cols - 1) // n_cols
            
            fig, axes = plt.subplots(n_rows, n_cols, figsize=(15, 5*n_rows))
            axes = axes.flatten() if n_rows > 1 else [axes] if n_cols == 1 else axes
            
            for idx, col in enumerate(self.categorical_columns[:n_rows*n_cols]):
                value_counts = self.df[col].value_counts().head(10)
                value_counts.plot(kind='bar', ax=axes[idx])
                axes[idx].set_title(f'Top 10 Values in {col}')
                axes[idx].set_xlabel(col)
                axes[idx].set_ylabel('Count')
                axes[idx].tick_params(axis='x', rotation=45)
            
            for idx in range(len(self.categorical_columns), len(axes)):
                axes[idx].axis('off')
            
            plt.tight_layout()
            if save_path:
                path = f"{save_path}/categorical_counts.png"
                plt.savefig(path, dpi=150, bbox_inches='tight')
                viz_paths.append(path)
            plt.close()
        
        self.results['visualizations'] = viz_paths
        return viz_paths
    
    def run_full_analysis(self, save_plots=False, plot_path=None):
        """Run complete EDA analysis"""
        print("Running comprehensive EDA analysis...")
        
        print("  - Gathering basic information...")
        self.get_basic_info()
        
        print("  - Calculating descriptive statistics...")
        self.get_descriptive_stats()
        
        print("  - Analyzing distributions...")
        self.analyze_distributions()
        
        print("  - Detecting outliers...")
        self.analyze_outliers()
        
        print("  - Calculating correlations...")
        self.calculate_correlations()
        
        print("  - Analyzing categorical variables...")
        self.analyze_categorical()
        
        if save_plots:
            print("  - Generating visualizations...")
            self.generate_visualizations(plot_path)
        
        print("EDA analysis complete!")
        return self.results


