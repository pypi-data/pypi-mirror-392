"""Data visualization utilities for SUTRA"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

class DataVisualizer:
    """Create visualizations from query results using Matplotlib and Seaborn"""
    
    def __init__(self):
        """Initialize the visualizer with default settings"""
        sns.set_style("whitegrid")
        self.figure_size = (10, 6)
        self.colors = sns.color_palette("husl", 10)
    
    def visualize(self, df: pd.DataFrame, query: str = ""):
        """
        Auto-detect and render best visualization for query results
        
        Args:
            df: DataFrame containing query results
            query: Original query string for context
        """
        if df is None or df.empty:
            print("⚠️ No data available for visualization")
            return
        
        # Show query context if provided
        if query:
            print(f"📊 Visualizing results for: {query}")
        
        # Identify numerical and categorical columns
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
        all_cols = df.columns.tolist()
        
        # Check if data is completely categorical
        if not num_cols and cat_cols:
            print("ℹ️ Dataset contains only categorical data - showing value counts")
            self._show_categorical_summary(df, cat_cols)
            return
        
        # Single row - just show as text
        if len(df) == 1:
            print("ℹ️ Single row result - no visualization needed")
            return
        
        # Handle based on number of columns
        if len(all_cols) == 1:
            self._visualize_single_column(df, all_cols[0], num_cols)
        elif len(all_cols) == 2:
            self._visualize_two_columns(df, num_cols, cat_cols)
        else:
            self._visualize_multiple_columns(df, num_cols, cat_cols, all_cols)
    
    def _visualize_single_column(self, df: pd.DataFrame, col: str, num_cols: list):
        """Handle visualization for single column data"""
        if col in num_cols:
            plt.figure(figsize=self.figure_size)
            plt.hist(df[col], bins=20, edgecolor='black', alpha=0.7)
            plt.xlabel(col)
            plt.ylabel('Frequency')
            plt.title(f'Distribution of {col}')
            plt.grid(True, alpha=0.3)
            plt.show()
    
    def _visualize_two_columns(self, df: pd.DataFrame, num_cols: list, cat_cols: list):
        """Handle visualization for two column data"""
        plt.figure(figsize=self.figure_size)
        
        if len(num_cols) == 2:  # Both numerical
            # Create scatter plot
            plt.scatter(df[num_cols[0]], df[num_cols[1]], alpha=0.6)
            plt.xlabel(num_cols[0])
            plt.ylabel(num_cols[1])
            plt.title(f'{num_cols[1]} vs {num_cols[0]}')
            
        elif len(num_cols) == 1 and len(cat_cols) == 1:  # One numerical, one categorical
            # Create bar plot
            grouped = df.groupby(cat_cols[0])[num_cols[0]].mean()
            grouped.plot(kind='bar', color=self.colors[0])
            plt.xlabel(cat_cols[0])
            plt.ylabel(f'Average {num_cols[0]}')
            plt.title(f'{num_cols[0]} by {cat_cols[0]}')
            plt.xticks(rotation=45, ha='right')
        
        plt.tight_layout()
        plt.show()
    
    def _visualize_multiple_columns(self, df: pd.DataFrame, num_cols: list, cat_cols: list, all_cols: list):
        """Handle visualization for three or more columns"""
        
        if not num_cols:
            print("⚠️ No numerical columns to visualize")
            return
        
        # Create subplots based on available data
        if len(num_cols) >= 2:
            # Create scatter matrix for numerical columns
            fig, axes = plt.subplots(1, 2, figsize=(15, 6))
            
            # Scatter plot of first two numerical columns
            axes[0].scatter(df[num_cols[0]], df[num_cols[1]], alpha=0.6)
            axes[0].set_xlabel(num_cols[0])
            axes[0].set_ylabel(num_cols[1])
            axes[0].set_title(f'{num_cols[1]} vs {num_cols[0]}')
            axes[0].grid(True, alpha=0.3)
            
            # Histogram of first numerical column
            axes[1].hist(df[num_cols[0]], bins=20, edgecolor='black', alpha=0.7)
            axes[1].set_xlabel(num_cols[0])
            axes[1].set_ylabel('Frequency')
            axes[1].set_title(f'Distribution of {num_cols[0]}')
            axes[1].grid(True, alpha=0.3)
            
        elif len(num_cols) == 1 and cat_cols:
            # Bar chart for categorical vs numerical
            plt.figure(figsize=self.figure_size)
            grouped = df.groupby(cat_cols[0])[num_cols[0]].mean()
            grouped.plot(kind='bar', color=self.colors[:len(grouped)])
            plt.xlabel(cat_cols[0])
            plt.ylabel(f'Average {num_cols[0]}')
            plt.title(f'{num_cols[0]} by {cat_cols[0]}')
            plt.xticks(rotation=45, ha='right')
        
        else:
            # Default to histogram
            plt.figure(figsize=self.figure_size)
            plt.hist(df[num_cols[0]], bins=20, edgecolor='black', alpha=0.7)
            plt.xlabel(num_cols[0])
            plt.ylabel('Frequency')
            plt.title(f'Distribution of {num_cols[0]}')
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    def _show_categorical_summary(self, df: pd.DataFrame, cat_cols: list):
        """Show summary for categorical data"""
        for col in cat_cols[:2]:  # Show first 2 categorical columns
            print(f"\nValue counts for {col}:")
            print(df[col].value_counts().head(10))
    
    def create_dashboard(self, df: pd.DataFrame, title: str = "Data Analysis Dashboard"):
        """Create a comprehensive dashboard with multiple visualizations"""
        num_cols = df.select_dtypes(include=['number']).columns.tolist()
        cat_cols = df.select_dtypes(exclude=['number']).columns.tolist()
        
        if not num_cols:
            print("⚠️ No numerical data for dashboard")
            return
        
        # Create figure with subplots
        fig = plt.figure(figsize=(15, 10))
        fig.suptitle(title, fontsize=16)
        
        plot_count = min(4, len(num_cols))
        
        for i, col in enumerate(num_cols[:plot_count]):
            plt.subplot(2, 2, i+1)
            plt.hist(df[col], bins=15, edgecolor='black', alpha=0.7, color=self.colors[i])
            plt.xlabel(col)
            plt.ylabel('Frequency')
            plt.title(f'Distribution of {col}')
            plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()