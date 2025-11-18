"""
Auto EDA - Main class for automatic Exploratory Data Analysis
"""

import pandas as pd
import numpy as np
import os
from .missing_value_handler import MissingValueHandler
from .eda_analyzer import EDAAnalyzer
from .report_generator import ReportGenerator


class AutoEDA:
    """
    Automatic Exploratory Data Analysis Library
    
    This class provides a completely automatic EDA workflow that:
    - Handles missing values intelligently
    - Performs comprehensive data analysis
    - Generates visualizations
    - Creates detailed reports
    - Interacts with user when needed
    """
    
    def __init__(self, df=None, file_path=None):
        """
        Initialize AutoEDA
        
        Parameters:
        -----------
        df : pandas.DataFrame, optional
            Input dataframe
        file_path : str, optional
            Path to CSV file to load
        """
        if df is not None:
            self.df = df.copy() if isinstance(df, pd.DataFrame) else pd.DataFrame(df)
        elif file_path is not None:
            self.df = self._load_data(file_path)
        else:
            raise ValueError("Either 'df' or 'file_path' must be provided")
        
        self.original_df = self.df.copy()
        self.missing_handler = None
        self.eda_analyzer = None
        self.report_generator = None
        self.strategies_applied = {}
        self.results = {}
        self.output_dir = None
        
    def _load_data(self, file_path):
        """Load data from file"""
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
            return pd.read_excel(file_path)
        elif file_path.endswith('.json'):
            return pd.read_json(file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_path}")
    
    def _ask_user(self, question, default=None, input_type=str):
        """
        Ask user a question and get input
        
        Parameters:
        -----------
        question : str
            Question to ask the user
        default : any, optional
            Default value if user presses Enter
        input_type : type
            Type to convert input to (str, int, float)
        """
        if default is not None:
            prompt = f"{question} (default: {default}): "
        else:
            prompt = f"{question}: "
        
        try:
            user_input = input(prompt).strip()
            if not user_input and default is not None:
                return default
            if not user_input:
                return self._ask_user(question, default, input_type)
            return input_type(user_input)
        except (ValueError, KeyboardInterrupt):
            if default is not None:
                print(f"Using default value: {default}")
                return default
            print("Invalid input. Please try again.")
            return self._ask_user(question, default, input_type)
    
    def _setup_output_directory(self):
        """Setup output directory for saving results"""
        if self.output_dir is None:
            use_output = self._ask_user(
                "Do you want to save EDA results to a directory? (yes/no)",
                default="yes"
            ).lower()
            
            if use_output in ['yes', 'y']:
                output_path = self._ask_user(
                    "Enter output directory path (press Enter for 'eda_output')",
                    default="eda_output"
                )
                self.output_dir = output_path
                os.makedirs(self.output_dir, exist_ok=True)
                print(f"Results will be saved to: {self.output_dir}")
            else:
                self.output_dir = None
    
    def handle_missing_values(self, auto=True):
        """
        Handle missing values in the dataset
        
        Parameters:
        -----------
        auto : bool
            If True, automatically decide strategies. If False, ask user.
        """
        print("\n" + "="*80)
        print("STEP 1: HANDLING MISSING VALUES")
        print("="*80)
        
        self.missing_handler = MissingValueHandler(self.df)
        missing_info = self.missing_handler.analyze_missing_values()
        
        if len(missing_info.get('counts', [])) == 0:
            print("✓ No missing values found in the dataset.")
            return self.df, {}
        
        print(f"\nFound missing values in {len(missing_info['counts'])} columns:")
        for col in missing_info['counts'].index:
            count = missing_info['counts'][col]
            pct = missing_info['percentages'][col]
            print(f"  - {col}: {count} missing ({pct:.2f}%)")
        
        if auto:
            print("\nAutomatically deciding strategies for handling missing values...")
            self.df, self.strategies_applied = self.missing_handler.handle_missing_values(auto=True)
            
            print("\nStrategies applied:")
            for col, strategy in self.strategies_applied.items():
                print(f"  - {col}: {strategy}")
        else:
            # Interactive mode - ask user for each column
            for col in missing_info['counts'].index:
                strategy = self._ask_user(
                    f"Choose strategy for '{col}' (mean/median/mode/drop/forward_fill/backward_fill)",
                    default="auto"
                )
                if strategy == "auto":
                    strategy = self.missing_handler.decide_strategy(col)
                
                self.strategies_applied[col] = strategy
                # Apply strategy
                if strategy == 'drop':
                    self.df = self.df.drop(columns=[col])
                elif strategy == 'mean':
                    self.df[col].fillna(self.df[col].mean(), inplace=True)
                elif strategy == 'median':
                    self.df[col].fillna(self.df[col].median(), inplace=True)
                elif strategy == 'mode':
                    mode_value = self.df[col].mode()
                    if len(mode_value) > 0:
                        self.df[col].fillna(mode_value[0], inplace=True)
                elif strategy == 'forward_fill':
                    self.df[col].ffill(inplace=True)
                    self.df[col].bfill(inplace=True)
                elif strategy == 'backward_fill':
                    self.df[col].bfill(inplace=True)
        
        print("\n✓ Missing values handled successfully!")
        return self.df, self.strategies_applied
    
    def perform_eda(self, save_plots=True):
        """
        Perform comprehensive EDA analysis
        
        Parameters:
        -----------
        save_plots : bool
            Whether to save visualization plots
        """
        print("\n" + "="*80)
        print("STEP 2: PERFORMING EXPLORATORY DATA ANALYSIS")
        print("="*80)
        
        self.eda_analyzer = EDAAnalyzer(self.df)
        plot_path = self.output_dir if save_plots and self.output_dir else None
        self.results = self.eda_analyzer.run_full_analysis(save_plots=save_plots, plot_path=plot_path)
        
        return self.results
    
    def generate_report(self, save_to_file=True):
        """
        Generate comprehensive EDA report
        
        Parameters:
        -----------
        save_to_file : bool
            Whether to save report to file
        """
        print("\n" + "="*80)
        print("STEP 3: GENERATING REPORT")
        print("="*80)
        
        missing_summary = self.missing_handler.get_summary() if self.missing_handler else {}
        
        self.report_generator = ReportGenerator(
            self.df,
            missing_summary,
            self.results,
            self.strategies_applied
        )
        
        report_text = self.report_generator.generate_text_report()
        
        # Print report to console
        print("\n" + report_text)
        
        # Save to file if requested
        if save_to_file and self.output_dir:
            report_path = os.path.join(self.output_dir, "eda_report.txt")
            self.report_generator.save_report(report_path)
            print(f"\n✓ Report saved to: {report_path}")
        
        return report_text
    
    def get_train_test_split(self, target_column=None, test_size=None, random_state=None):
        """
        Get train-test split with user interaction
        
        Parameters:
        -----------
        target_column : str, optional
            Target column name
        test_size : float, optional
            Test set size (0.0 to 1.0)
        random_state : int, optional
            Random state for reproducibility
        """
        print("\n" + "="*80)
        print("STEP 4: TRAIN-TEST SPLIT")
        print("="*80)
        
        # Ask for target column if not provided
        if target_column is None:
            print("\nAvailable columns:")
            for i, col in enumerate(self.df.columns, 1):
                print(f"  {i}. {col}")
            target_col_idx = self._ask_user(
                "\nEnter target column number or name",
                input_type=str
            )
            # Try to convert to int and get by index, otherwise use as name
            try:
                target_column = self.df.columns[int(target_col_idx) - 1]
            except (ValueError, IndexError):
                target_column = target_col_idx
        
        if target_column not in self.df.columns:
            raise ValueError(f"Column '{target_column}' not found in dataset")
        
        # Ask for test size if not provided
        if test_size is None:
            test_size = self._ask_user(
                "Enter test set size (0.0 to 1.0)",
                default=0.2,
                input_type=float
            )
        
        # Ask for random state if not provided
        if random_state is None:
            use_random_state = self._ask_user(
                "Do you want to set a random state for reproducibility? (yes/no)",
                default="yes"
            ).lower()
            if use_random_state in ['yes', 'y']:
                random_state = self._ask_user(
                    "Enter random state (integer)",
                    default=42,
                    input_type=int
                )
        
        # Perform split
        from sklearn.model_selection import train_test_split
        
        X = self.df.drop(columns=[target_column])
        y = self.df[target_column]
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        print(f"\n✓ Train-Test Split Complete!")
        print(f"  Training set: {X_train.shape[0]} samples ({1-test_size:.1%})")
        print(f"  Test set: {X_test.shape[0]} samples ({test_size:.1%})")
        
        return X_train, X_test, y_train, y_test
    
    def run_complete_eda(self, auto_handle_missing=True, save_plots=True, save_report=True, 
                        get_split=False, target_column=None):
        """
        Run complete automatic EDA workflow
        
        Parameters:
        -----------
        auto_handle_missing : bool
            Automatically handle missing values
        save_plots : bool
            Save visualization plots
        save_report : bool
            Save report to file
        get_split : bool
            Whether to perform train-test split
        target_column : str, optional
            Target column for train-test split
        """
        print("\n" + "="*80)
        print("AUTOMATIC EDA WORKFLOW")
        print("="*80)
        print(f"Dataset shape: {self.df.shape}")
        print(f"Columns: {len(self.df.columns)}")
        
        # Setup output directory
        self._setup_output_directory()
        
        # Step 1: Handle missing values
        self.handle_missing_values(auto=auto_handle_missing)
        
        # Step 2: Perform EDA
        self.perform_eda(save_plots=save_plots)
        
        # Step 3: Generate report
        self.generate_report(save_to_file=save_report)
        
        # Step 4: Train-test split (optional)
        split_data = None
        if get_split:
            split_data = self.get_train_test_split(target_column=target_column)
        
        print("\n" + "="*80)
        print("EDA WORKFLOW COMPLETE!")
        print("="*80)
        print("\nYour dataset is now ready for model building!")
        if split_data:
            print("Train-test split has been performed.")
        print(f"\nCleaned dataset shape: {self.df.shape}")
        print(f"Original dataset shape: {self.original_df.shape}")
        
        return {
            'cleaned_df': self.df,
            'original_df': self.original_df,
            'results': self.results,
            'strategies_applied': self.strategies_applied,
            'split_data': split_data
        }
    
    def get_cleaned_dataframe(self):
        """Get the cleaned dataframe after EDA"""
        return self.df
    
    def get_results(self):
        """Get all EDA results"""
        return self.results

