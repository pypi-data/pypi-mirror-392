"""
Report Generator - Creates comprehensive summary reports
"""

import pandas as pd
from datetime import datetime


class ReportGenerator:
    """Generates comprehensive EDA reports"""
    
    def __init__(self, df, missing_handler_summary, eda_results, strategies_applied):
        self.df = df
        self.missing_handler_summary = missing_handler_summary
        self.eda_results = eda_results
        self.strategies_applied = strategies_applied
        self.report = []
    
    def generate_text_report(self):
        """Generate a comprehensive text report"""
        report_lines = []
        
        # Header
        report_lines.append("=" * 80)
        report_lines.append("AUTOMATIC EDA REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Dataset Overview
        report_lines.append("1. DATASET OVERVIEW")
        report_lines.append("-" * 80)
        basic_info = self.eda_results.get('basic_info', {})
        report_lines.append(f"  Shape: {basic_info.get('shape', 'N/A')}")
        report_lines.append(f"  Total Rows: {basic_info.get('shape', (0, 0))[0]}")
        report_lines.append(f"  Total Columns: {basic_info.get('shape', (0, 0))[1]}")
        report_lines.append(f"  Memory Usage: {basic_info.get('memory_usage', 0):.2f} MB")
        report_lines.append("")
        
        # Column Information
        report_lines.append("2. COLUMN INFORMATION")
        report_lines.append("-" * 80)
        report_lines.append(f"  Numeric Columns ({len(basic_info.get('numeric_columns', []))}): {', '.join(basic_info.get('numeric_columns', []))}")
        report_lines.append(f"  Categorical Columns ({len(basic_info.get('categorical_columns', []))}): {', '.join(basic_info.get('categorical_columns', []))}")
        if basic_info.get('datetime_columns'):
            report_lines.append(f"  Datetime Columns ({len(basic_info.get('datetime_columns', []))}): {', '.join(basic_info.get('datetime_columns', []))}")
        report_lines.append("")
        
        # Missing Values
        report_lines.append("3. MISSING VALUE HANDLING")
        report_lines.append("-" * 80)
        missing_info = self.missing_handler_summary.get('missing_info', {})
        if missing_info.get('counts') is not None and len(missing_info['counts']) > 0:
            report_lines.append("  Missing values found and handled:")
            for col in missing_info['counts'].index:
                count = missing_info['counts'][col]
                pct = missing_info['percentages'][col]
                strategy = self.strategies_applied.get(col, 'N/A')
                report_lines.append(f"    - {col}: {count} ({pct:.2f}%) -> Strategy: {strategy}")
        else:
            report_lines.append("  No missing values found in the dataset.")
        report_lines.append("")
        
        # Descriptive Statistics
        report_lines.append("4. DESCRIPTIVE STATISTICS")
        report_lines.append("-" * 80)
        desc_stats = self.eda_results.get('descriptive_stats', {})
        numeric_stats = desc_stats.get('numeric', {})
        if numeric_stats:
            report_lines.append("  Numeric Columns Summary:")
            for col in list(numeric_stats.keys())[:5]:  # Show first 5 columns
                stats = numeric_stats[col]
                report_lines.append(f"    {col}:")
                report_lines.append(f"      Mean: {stats.get('mean', 'N/A'):.2f}")
                report_lines.append(f"      Median: {stats.get('50%', 'N/A'):.2f}")
                report_lines.append(f"      Std: {stats.get('std', 'N/A'):.2f}")
                report_lines.append(f"      Min: {stats.get('min', 'N/A'):.2f}")
                report_lines.append(f"      Max: {stats.get('max', 'N/A'):.2f}")
        report_lines.append("")
        
        # Outliers
        report_lines.append("5. OUTLIER ANALYSIS")
        report_lines.append("-" * 80)
        outliers = self.eda_results.get('outliers', {})
        for col, outlier_info in list(outliers.items())[:5]:  # Show first 5 columns
            report_lines.append(f"  {col}:")
            report_lines.append(f"    Outlier Count: {outlier_info['count']}")
            report_lines.append(f"    Outlier Percentage: {outlier_info['percentage']:.2f}%")
        report_lines.append("")
        
        # Correlations
        report_lines.append("6. CORRELATION ANALYSIS")
        report_lines.append("-" * 80)
        correlations = self.eda_results.get('correlations', {})
        high_corr = correlations.get('high_correlation_pairs', [])
        if high_corr:
            report_lines.append("  Highly Correlated Pairs (|r| > 0.7):")
            for pair in high_corr[:10]:  # Show top 10
                report_lines.append(f"    {pair['column1']} <-> {pair['column2']}: {pair['correlation']:.3f}")
        else:
            report_lines.append("  No highly correlated pairs found.")
        report_lines.append("")
        
        # Distributions
        report_lines.append("7. DISTRIBUTION ANALYSIS")
        report_lines.append("-" * 80)
        distributions = self.eda_results.get('distributions', {})
        for col, dist_info in list(distributions.items())[:5]:  # Show first 5 columns
            report_lines.append(f"  {col}:")
            report_lines.append(f"    Skewness: {dist_info['skewness']:.3f}")
            report_lines.append(f"    Kurtosis: {dist_info['kurtosis']:.3f}")
            report_lines.append(f"    Normal Distribution: {dist_info['is_normal']}")
        report_lines.append("")
        
        # Categorical Analysis
        report_lines.append("8. CATEGORICAL VARIABLE ANALYSIS")
        report_lines.append("-" * 80)
        categorical = self.eda_results.get('categorical', {})
        for col, cat_info in list(categorical.items())[:5]:  # Show first 5 columns
            report_lines.append(f"  {col}:")
            report_lines.append(f"    Unique Values: {cat_info['unique_count']}")
            report_lines.append(f"    Most Frequent: {cat_info['most_frequent']} ({cat_info['most_frequent_count']} times)")
        report_lines.append("")
        
        # Recommendations
        report_lines.append("9. RECOMMENDATIONS")
        report_lines.append("-" * 80)
        recommendations = self._generate_recommendations()
        for i, rec in enumerate(recommendations, 1):
            report_lines.append(f"  {i}. {rec}")
        report_lines.append("")
        
        # Footer
        report_lines.append("=" * 80)
        report_lines.append("END OF REPORT")
        report_lines.append("=" * 80)
        
        return "\n".join(report_lines)
    
    def _generate_recommendations(self):
        """Generate recommendations based on the analysis"""
        recommendations = []
        
        # Check for missing values
        missing_info = self.missing_handler_summary.get('missing_info', {})
        if missing_info.get('counts') is not None and len(missing_info['counts']) > 0:
            recommendations.append("Missing values have been handled. Review the strategies applied.")
        
        # Check for outliers
        outliers = self.eda_results.get('outliers', {})
        high_outlier_cols = [col for col, info in outliers.items() if info['percentage'] > 5]
        if high_outlier_cols:
            recommendations.append(f"High number of outliers detected in: {', '.join(high_outlier_cols)}. Consider outlier treatment.")
        
        # Check for high correlations
        correlations = self.eda_results.get('correlations', {})
        high_corr = correlations.get('high_correlation_pairs', [])
        if high_corr:
            recommendations.append("Highly correlated features detected. Consider feature selection to avoid multicollinearity.")
        
        # Check for skewed distributions
        distributions = self.eda_results.get('distributions', {})
        skewed_cols = [col for col, info in distributions.items() if abs(info['skewness']) > 1]
        if skewed_cols:
            recommendations.append(f"Skewed distributions found in: {', '.join(skewed_cols)}. Consider transformation (log, sqrt, etc.).")
        
        # General recommendations
        recommendations.append("Dataset is ready for model building. Consider train-test split before proceeding.")
        recommendations.append("For classification tasks, check class balance. For regression, verify target distribution.")
        
        return recommendations
    
    def save_report(self, filepath):
        """Save the report to a file"""
        report_text = self.generate_text_report()
        with open(filepath, 'w') as f:
            f.write(report_text)
        return filepath


