"""
Dataset Analysis Script for German Credit Dataset
Analyzes size, attribute types, value ranges, sparsity, outliers, missing values, and correlations
"""

import pandas as pd
import numpy as np
from scipy.io import arff
from scipy import stats
import os

def load_data():
    """Load the credit-g dataset"""
    data_path = os.path.join("data")
    data = arff.loadarff(os.path.join(data_path, "credit-g.arff"))
    df = pd.DataFrame(data[0])
    
    # Decode byte strings in object columns
    for col in df.select_dtypes([object]).columns:
        df[col] = df[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
    
    return df

def analyze_dataset_characteristics(df):
    """Comprehensive dataset analysis"""
    
    print("=" * 80)
    print("GERMAN CREDIT DATASET - COMPREHENSIVE ANALYSIS")
    print("=" * 80)
    
    # 1. SIZE
    print("\n1. DATASET SIZE")
    print("-" * 80)
    print(f"Number of samples: {df.shape[0]}")
    print(f"Number of features: {df.shape[1] - 1}")  # Excluding target
    print(f"Total data points: {df.shape[0] * df.shape[1]}")
    print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
    
    # 2. ATTRIBUTE TYPES
    print("\n2. ATTRIBUTE TYPES")
    print("-" * 80)
    print(f"\nData types:\n{df.dtypes.value_counts()}\n")
    
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=[object]).columns.tolist()
    
    print(f"Numerical attributes ({len(numerical_cols)}): {numerical_cols}")
    print(f"\nCategorical attributes ({len(categorical_cols)}): {categorical_cols}")
    
    # Detailed attribute classification
    print("\nAttribute Classification:")
    for col in df.columns:
        unique_count = df[col].nunique()
        dtype = df[col].dtype
        if dtype == 'object':
            print(f"  {col}: Categorical/Nominal ({unique_count} unique values)")
        elif dtype in ['int64', 'float64']:
            if unique_count <= 10:
                print(f"  {col}: Discrete/Ordinal ({unique_count} unique values)")
            else:
                print(f"  {col}: Continuous ({unique_count} unique values)")
    
    # 3. VALUE RANGES & MIN/MAX
    print("\n3. VALUE RANGES (Numerical Features)")
    print("-" * 80)
    if numerical_cols:
        stats_df = df[numerical_cols].describe().T
        stats_df['range'] = stats_df['max'] - stats_df['min']
        print(stats_df[['min', 'max', 'range', 'mean', 'std']])
    
    print("\n   CATEGORICAL FEATURE VALUE COUNTS")
    print("-" * 80)
    for col in categorical_cols:
        print(f"\n{col}:")
        print(df[col].value_counts().to_string())
    
    # 4. SPARSITY
    print("\n4. SPARSITY ANALYSIS")
    print("-" * 80)
    # For numerical columns, count zeros as potential sparse indicators
    if numerical_cols:
        zero_counts = (df[numerical_cols] == 0).sum()
        sparsity_pct = (zero_counts / len(df)) * 100
        sparsity_df = pd.DataFrame({
            'Zero Count': zero_counts,
            'Sparsity %': sparsity_pct
        })
        print(sparsity_df[sparsity_df['Sparsity %'] > 0])
    else:
        print("No numerical columns for sparsity analysis")
    
    # 5. MISSING VALUES
    print("\n5. MISSING VALUES")
    print("-" * 80)
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    missing_df = pd.DataFrame({
        'Missing Count': missing,
        'Missing %': missing_pct
    })
    if missing.sum() > 0:
        print(missing_df[missing_df['Missing Count'] > 0])
    else:
        print("No missing values detected in the dataset!")
    
    # 6. OUTLIERS (using IQR method for numerical features)
    print("\n6. OUTLIER DETECTION (IQR Method)")
    print("-" * 80)
    if numerical_cols:
        outlier_summary = []
        for col in numerical_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
            outlier_count = len(outliers)
            outlier_pct = (outlier_count / len(df)) * 100
            
            outlier_summary.append({
                'Feature': col,
                'Lower Bound': lower_bound,
                'Upper Bound': upper_bound,
                'Outlier Count': outlier_count,
                'Outlier %': outlier_pct
            })
        
        outlier_df = pd.DataFrame(outlier_summary)
        print(outlier_df[outlier_df['Outlier Count'] > 0].to_string(index=False))
        
        # Z-score method (alternative)
        print("\n   OUTLIERS (Z-Score > 3)")
        print("-" * 80)
        z_scores = np.abs(stats.zscore(df[numerical_cols]))
        outliers_zscore = (z_scores > 3).sum(axis=0)
        if outliers_zscore.sum() > 0:
            print(pd.DataFrame({
                'Feature': numerical_cols,
                'Outliers (|z| > 3)': outliers_zscore
            })[outliers_zscore > 0].to_string(index=False))
        else:
            print("No outliers detected using Z-score method")
    
    # 7. CORRELATIONS
    print("\n7. CORRELATION ANALYSIS")
    print("-" * 80)
    if numerical_cols and len(numerical_cols) > 1:
        corr_matrix = df[numerical_cols].corr()
        print("\nCorrelation Matrix:")
        print(corr_matrix)
        
        # Find high correlations (excluding diagonal)
        print("\n   HIGH CORRELATIONS (|r| > 0.5):")
        print("-" * 80)
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                if abs(corr_matrix.iloc[i, j]) > 0.5:
                    high_corr.append({
                        'Feature 1': corr_matrix.columns[i],
                        'Feature 2': corr_matrix.columns[j],
                        'Correlation': corr_matrix.iloc[i, j]
                    })
        
        if high_corr:
            high_corr_df = pd.DataFrame(high_corr)
            print(high_corr_df.to_string(index=False))
        else:
            print("No high correlations (|r| > 0.5) found between numerical features")
    
    # 8. CLASS DISTRIBUTION (Target Variable)
    print("\n8. TARGET CLASS DISTRIBUTION")
    print("-" * 80)
    if 'class' in df.columns:
        class_counts = df['class'].value_counts()
        class_pcts = (class_counts / len(df)) * 100
        class_df = pd.DataFrame({
            'Count': class_counts,
            'Percentage': class_pcts
        })
        print(class_df)
        
        # Calculate imbalance ratio
        imbalance_ratio = class_counts.max() / class_counts.min()
        print(f"\nClass Imbalance Ratio: {imbalance_ratio:.2f}:1")
        if imbalance_ratio > 1.5:
            print("⚠ Dataset has class imbalance (majority class dominates)")
    
    # 9. SUMMARY STATISTICS
    print("\n9. SUMMARY STATISTICS")
    print("-" * 80)
    print(df.describe(include='all').T)
    
    print("\n" + "=" * 80)
    print("ANALYSIS COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    # Load data
    df = load_data()
    
    # Run comprehensive analysis
    analyze_dataset_characteristics(df)
