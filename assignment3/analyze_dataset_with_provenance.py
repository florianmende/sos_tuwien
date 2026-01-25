"""
Dataset Analysis Script with PROV-O Documentation
Analyzes the German Credit dataset and generates provenance triples
"""

import pandas as pd
import numpy as np
from scipy.io import arff
from scipy import stats
import os
import datetime
import json
import matplotlib.pyplot as plt
import seaborn as sns

# Configuration
executed_by = 'stud-id_12017067'
student_a = 'stud-id_12017067'
code_writer_role = 'code_writer'
code_executor_role = 'code_executor'

def now() -> str:
    """Returns the current time in ISO 8601 format with UTC timezone"""
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    timestamp_formated = timestamp.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    return timestamp_formated

def load_data():
    """Load the credit-g dataset"""
    data_path = os.path.join("data")
    data = arff.loadarff(os.path.join(data_path, "credit-g.arff"))
    df = pd.DataFrame(data[0])
    
    # Decode byte strings in object columns
    for col in df.select_dtypes([object]).columns:
        df[col] = df[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)
    
    return df

# Storage for all provenance triples
all_provenance_triples = []

print("=" * 80)
print("GERMAN CREDIT DATASET - ANALYSIS WITH PROVENANCE DOCUMENTATION")
print("=" * 80)

# Load data
df = load_data()

# Create data analysis phase activity
data_analysis_phase = [
    ':data_analysis_phase rdf:type prov:Activity .',
    ':data_analysis_phase rdfs:label "Data Analysis Phase" .',
    ':data_analysis_phase rdfs:comment "Comprehensive analysis of the German Credit dataset characteristics" .',
]
all_provenance_triples.extend(data_analysis_phase)

#############################################
# 1) SIZE ANALYSIS
#############################################
print("\n" + "=" * 80)
print("1. DATASET SIZE ANALYSIS")
print("=" * 80)

def get_data_size(df):
    """Get dataset size (rows, columns)"""
    return {"rows": df.shape[0], "columns": df.shape[1], "total_cells": df.shape[0] * df.shape[1]}

start_time_data_size = now()
data_size_report = get_data_size(df)
print(f"Data size: {data_size_report}")
end_time_data_size = now()

# Activity: Check and create report
check_size_uuid_executor = "9f0dc14f-b18c-462c-97d0-e7582aaf19db"
check_size_uuid_writer = "66f0171b-eef4-4a71-b878-b28fea0a0133"

check_size_activity = [
    ':check_size rdf:type prov:Activity .',
    ':check_size sc:isPartOf :data_analysis_phase .',
    ':check_size rdfs:comment "Check data size" .',
    ':check_size rdfs:comment "Inspect the shape of the loaded dataset to determine the number of records and features." .',
    f':check_size prov:startedAtTime "{start_time_data_size}"^^xsd:dateTime .',
    f':check_size prov:endedAtTime "{end_time_data_size}"^^xsd:dateTime .',
    f':check_size prov:qualifiedAssociation :{check_size_uuid_executor} .',
    f':{check_size_uuid_executor} prov:agent :{executed_by} .',
    f':{check_size_uuid_executor} rdf:type prov:Association .',
    f':{check_size_uuid_executor} prov:hadRole :{code_executor_role} .',
    f':check_size prov:qualifiedAssociation :{check_size_uuid_writer} .',
    f':{check_size_uuid_writer} prov:agent :{student_a} .',
    f':{check_size_uuid_writer} rdf:type prov:Association .',
    f':{check_size_uuid_writer} prov:hadRole :{code_writer_role} .',
    ':check_size prov:used :raw_data .',
    ':check_size_report rdf:type prov:Entity .',
    f':check_size_report rdfs:comment "Dataset contains {data_size_report["rows"]} rows and {data_size_report["columns"]} columns" .',
    ':check_size_report prov:wasGeneratedBy :check_size .',
]
all_provenance_triples.extend(check_size_activity)

# Inspect activity outcome and derive decisions
insp_size_uuid_executor = "d3f5e1b3-4f3a-4e2e-9a1b-8c4f2c3b5e6f"

inspect_size_report_activity = [
    ':inspect_size_report rdf:type prov:Activity .',
    ':inspect_size_report rdfs:comment "Inspect the dataset size" .',
    f':inspect_size_report rdfs:comment "The dataset contains {data_size_report["rows"]} rows and {data_size_report["columns"]} dimensions of which one is the target variable. Dataset size is manageable for SOM training without subsampling." .',
    f':inspect_size_report prov:startedAtTime "{start_time_data_size}"^^xsd:dateTime .',
    f':inspect_size_report prov:endedAtTime "{end_time_data_size}"^^xsd:dateTime .',
    f':inspect_size_report prov:qualifiedAssociation :{insp_size_uuid_executor} .',
    f':{insp_size_uuid_executor} prov:agent :{student_a} .',
    f':{insp_size_uuid_executor} rdf:type prov:Association .',
    f':{insp_size_uuid_executor} prov:hadRole :{code_executor_role} .',
    ':inspect_size_report prov:used :check_size_report .',
]
all_provenance_triples.extend(inspect_size_report_activity)

#############################################
# 2) ATTRIBUTE TYPES ANALYSIS
#############################################
print("\n" + "=" * 80)
print("2. ATTRIBUTE TYPES ANALYSIS")
print("=" * 80)

def get_attribute_types(df):
    """Analyze attribute types"""
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=[object]).columns.tolist()
    
    type_details = {}
    for col in df.columns:
        unique_count = df[col].nunique()
        dtype = str(df[col].dtype)
        if dtype == 'object':
            type_details[col] = {"type": "categorical", "unique_values": unique_count}
        elif dtype in ['int64', 'float64']:
            if unique_count <= 10:
                type_details[col] = {"type": "discrete", "unique_values": unique_count}
            else:
                type_details[col] = {"type": "continuous", "unique_values": unique_count}
    
    return {
        "numerical_count": len(numerical_cols),
        "categorical_count": len(categorical_cols),
        "type_details": type_details
    }

start_time_attr_types = now()
attr_types_report = get_attribute_types(df)
print(f"Numerical attributes: {attr_types_report['numerical_count']}")
print(f"Categorical attributes: {attr_types_report['categorical_count']}")
end_time_attr_types = now()

# Activity: Analyze attribute types
check_types_uuid_executor = "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d"
check_types_uuid_writer = "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e"

check_types_activity = [
    ':check_attribute_types rdf:type prov:Activity .',
    ':check_attribute_types sc:isPartOf :data_analysis_phase .',
    ':check_attribute_types rdfs:comment "Analyze attribute types" .',
    ':check_attribute_types rdfs:comment "Classify each feature as numerical (continuous/discrete) or categorical to understand data structure." .',
    f':check_attribute_types prov:startedAtTime "{start_time_attr_types}"^^xsd:dateTime .',
    f':check_attribute_types prov:endedAtTime "{end_time_attr_types}"^^xsd:dateTime .',
    f':check_attribute_types prov:qualifiedAssociation :{check_types_uuid_executor} .',
    f':{check_types_uuid_executor} prov:agent :{executed_by} .',
    f':{check_types_uuid_executor} rdf:type prov:Association .',
    f':{check_types_uuid_executor} prov:hadRole :{code_executor_role} .',
    f':check_attribute_types prov:qualifiedAssociation :{check_types_uuid_writer} .',
    f':{check_types_uuid_writer} prov:agent :{student_a} .',
    f':{check_types_uuid_writer} rdf:type prov:Association .',
    f':{check_types_uuid_writer} prov:hadRole :{code_writer_role} .',
    ':check_attribute_types prov:used :raw_data .',
    ':attribute_types_report rdf:type prov:Entity .',
    f':attribute_types_report rdfs:comment "Found {attr_types_report["numerical_count"]} numerical and {attr_types_report["categorical_count"]} categorical attributes" .',
    ':attribute_types_report prov:wasGeneratedBy :check_attribute_types .',
]
all_provenance_triples.extend(check_types_activity)

# Inspect attribute types
insp_types_uuid_executor = "c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f"

inspect_types_activity = [
    ':inspect_attribute_types rdf:type prov:Activity .',
    ':inspect_attribute_types rdfs:comment "Inspect attribute types distribution" .',
    f':inspect_attribute_types rdfs:comment "Dataset has mixed types with {attr_types_report["numerical_count"]} numerical and {attr_types_report["categorical_count"]} categorical features. Categorical features will require encoding for SOM training." .',
    f':inspect_attribute_types prov:startedAtTime "{start_time_attr_types}"^^xsd:dateTime .',
    f':inspect_attribute_types prov:endedAtTime "{end_time_attr_types}"^^xsd:dateTime .',
    f':inspect_attribute_types prov:qualifiedAssociation :{insp_types_uuid_executor} .',
    f':{insp_types_uuid_executor} prov:agent :{student_a} .',
    f':{insp_types_uuid_executor} rdf:type prov:Association .',
    f':{insp_types_uuid_executor} prov:hadRole :{code_executor_role} .',
    ':inspect_attribute_types prov:used :attribute_types_report .',
    ':decision_encode_categorical rdf:type prov:Entity .',
    ':decision_encode_categorical rdfs:comment "Decision: Apply ordinal encoding to categorical variables preserving meaningful order where applicable" .',
    ':decision_encode_categorical prov:wasGeneratedBy :inspect_attribute_types .',
]
all_provenance_triples.extend(inspect_types_activity)

#############################################
# 3) VALUE RANGES ANALYSIS
#############################################
print("\n" + "=" * 80)
print("3. VALUE RANGES ANALYSIS")
print("=" * 80)

def get_value_ranges(df):
    """Analyze value ranges for numerical features"""
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    ranges = {}
    for col in numerical_cols:
        ranges[col] = {
            "min": float(df[col].min()),
            "max": float(df[col].max()),
            "range": float(df[col].max() - df[col].min()),
            "mean": float(df[col].mean()),
            "std": float(df[col].std())
        }
    return ranges

start_time_ranges = now()
ranges_report = get_value_ranges(df)
print(f"Analyzed value ranges for {len(ranges_report)} numerical features")
for col, stats in ranges_report.items():
    print(f"  {col}: [{stats['min']:.2f}, {stats['max']:.2f}], range={stats['range']:.2f}")
end_time_ranges = now()

# Activity: Analyze value ranges
check_ranges_uuid_executor = "d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f8a"
check_ranges_uuid_writer = "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b"

check_ranges_activity = [
    ':check_value_ranges rdf:type prov:Activity .',
    ':check_value_ranges sc:isPartOf :data_analysis_phase .',
    ':check_value_ranges rdfs:comment "Analyze value ranges" .',
    ':check_value_ranges rdfs:comment "Determine min, max, and range for numerical features to understand data distribution and scaling needs." .',
    f':check_value_ranges prov:startedAtTime "{start_time_ranges}"^^xsd:dateTime .',
    f':check_value_ranges prov:endedAtTime "{end_time_ranges}"^^xsd:dateTime .',
    f':check_value_ranges prov:qualifiedAssociation :{check_ranges_uuid_executor} .',
    f':{check_ranges_uuid_executor} prov:agent :{executed_by} .',
    f':{check_ranges_uuid_executor} rdf:type prov:Association .',
    f':{check_ranges_uuid_executor} prov:hadRole :{code_executor_role} .',
    f':check_value_ranges prov:qualifiedAssociation :{check_ranges_uuid_writer} .',
    f':{check_ranges_uuid_writer} prov:agent :{student_a} .',
    f':{check_ranges_uuid_writer} rdf:type prov:Association .',
    f':{check_ranges_uuid_writer} prov:hadRole :{code_writer_role} .',
    ':check_value_ranges prov:used :raw_data .',
    ':value_ranges_report rdf:type prov:Entity .',
    f':value_ranges_report rdfs:comment "Analyzed ranges for {len(ranges_report)} numerical features with varying scales" .',
    ':value_ranges_report prov:wasGeneratedBy :check_value_ranges .',
]
all_provenance_triples.extend(check_ranges_activity)

# Inspect value ranges
insp_ranges_uuid_executor = "f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c"

inspect_ranges_activity = [
    ':inspect_value_ranges rdf:type prov:Activity .',
    ':inspect_value_ranges rdfs:comment "Inspect value ranges" .',
    ':inspect_value_ranges rdfs:comment "Features have different scales (e.g., age 19-75, credit_amount 250-18424, duration 4-72). Different scales require normalization for SOM training to prevent features with larger ranges from dominating distance calculations." .',
    f':inspect_value_ranges prov:startedAtTime "{start_time_ranges}"^^xsd:dateTime .',
    f':inspect_value_ranges prov:endedAtTime "{end_time_ranges}"^^xsd:dateTime .',
    f':inspect_value_ranges prov:qualifiedAssociation :{insp_ranges_uuid_executor} .',
    f':{insp_ranges_uuid_executor} prov:agent :{student_a} .',
    f':{insp_ranges_uuid_executor} rdf:type prov:Association .',
    f':{insp_ranges_uuid_executor} prov:hadRole :{code_executor_role} .',
    ':inspect_value_ranges prov:used :value_ranges_report .',
    ':decision_normalize_data rdf:type prov:Entity .',
    ':decision_normalize_data rdfs:comment "Decision: Apply MinMax scaling to normalize all features to [0,1] range for fair distance computation in SOM" .',
    ':decision_normalize_data prov:wasGeneratedBy :inspect_value_ranges .',
]
all_provenance_triples.extend(inspect_ranges_activity)

#############################################
# 4) MISSING VALUES ANALYSIS
#############################################
print("\n" + "=" * 80)
print("4. MISSING VALUES ANALYSIS")
print("=" * 80)

def check_missing_values(df):
    """Check for missing values"""
    missing = df.isnull().sum()
    missing_pct = (missing / len(df)) * 100
    return {
        "total_missing": int(missing.sum()),
        "columns_with_missing": list(missing[missing > 0].index),
        "missing_percentages": {col: float(pct) for col, pct in missing_pct[missing_pct > 0].items()}
    }

start_time_missing = now()
missing_report = check_missing_values(df)
print(f"Total missing values: {missing_report['total_missing']}")
if missing_report['total_missing'] == 0:
    print("✓ No missing values detected in the dataset")
end_time_missing = now()

# Activity: Check missing values
check_missing_uuid_executor = "a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d"
check_missing_uuid_writer = "b8c9d0e1-f2a3-4b4c-5d6e-7f8a9b0c1d2e"

check_missing_activity = [
    ':check_missing_values rdf:type prov:Activity .',
    ':check_missing_values sc:isPartOf :data_analysis_phase .',
    ':check_missing_values rdfs:comment "Check for missing values" .',
    ':check_missing_values rdfs:comment "Identify any missing or null values in the dataset that may require imputation or removal." .',
    f':check_missing_values prov:startedAtTime "{start_time_missing}"^^xsd:dateTime .',
    f':check_missing_values prov:endedAtTime "{end_time_missing}"^^xsd:dateTime .',
    f':check_missing_values prov:qualifiedAssociation :{check_missing_uuid_executor} .',
    f':{check_missing_uuid_executor} prov:agent :{executed_by} .',
    f':{check_missing_uuid_executor} rdf:type prov:Association .',
    f':{check_missing_uuid_executor} prov:hadRole :{code_executor_role} .',
    f':check_missing_values prov:qualifiedAssociation :{check_missing_uuid_writer} .',
    f':{check_missing_uuid_writer} prov:agent :{student_a} .',
    f':{check_missing_uuid_writer} rdf:type prov:Association .',
    f':{check_missing_uuid_writer} prov:hadRole :{code_writer_role} .',
    ':check_missing_values prov:used :raw_data .',
    ':missing_values_report rdf:type prov:Entity .',
    f':missing_values_report rdfs:comment "Found {missing_report["total_missing"]} missing values in dataset" .',
    ':missing_values_report prov:wasGeneratedBy :check_missing_values .',
]
all_provenance_triples.extend(check_missing_activity)

# Inspect missing values
insp_missing_uuid_executor = "c9d0e1f2-a3b4-4c5d-6e7f-8a9b0c1d2e3f"

inspect_missing_activity = [
    ':inspect_missing_values rdf:type prov:Activity .',
    ':inspect_missing_values rdfs:comment "Inspect missing values" .',
    ':inspect_missing_values rdfs:comment "No missing values detected in the dataset. Data is complete and ready for analysis without imputation." .',
    f':inspect_missing_values prov:startedAtTime "{start_time_missing}"^^xsd:dateTime .',
    f':inspect_missing_values prov:endedAtTime "{end_time_missing}"^^xsd:dateTime .',
    f':inspect_missing_values prov:qualifiedAssociation :{insp_missing_uuid_executor} .',
    f':{insp_missing_uuid_executor} prov:agent :{student_a} .',
    f':{insp_missing_uuid_executor} rdf:type prov:Association .',
    f':{insp_missing_uuid_executor} prov:hadRole :{code_executor_role} .',
    ':inspect_missing_values prov:used :missing_values_report .',
]
all_provenance_triples.extend(inspect_missing_activity)

#############################################
# 5) OUTLIER DETECTION
#############################################
print("\n" + "=" * 80)
print("5. OUTLIER DETECTION (IQR Method)")
print("=" * 80)

def detect_outliers_iqr(
    df,
    plot: bool = True,
    save_dir: str | None = os.path.join("pics", "outliers"),
    show: bool = False,
    max_plots: int = 20,
):
    """Detect outliers using IQR method and optionally plot affected columns.

    Parameters:
    - df: Input DataFrame
    - plot: If True, generate plots for columns with outliers
    - save_dir: Directory to save plots (created if missing). Defaults to pics/outliers
    - show: If True, display plots interactively
    - max_plots: Limit number of plots generated to avoid excessive output

    Returns:
    - Dict with per-column outlier summary (count, percentage, bounds, plot_path)
    """
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    outlier_summary = {}

    # Prepare plotting directory if plotting is enabled
    plots_done = 0
    if plot and save_dir:
        os.makedirs(save_dir, exist_ok=True)

    for col in numerical_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1

        # Skip plotting for non-varying columns
        if IQR == 0:
            lower_bound = Q1
            upper_bound = Q3
        else:
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)][col]
        outlier_count = len(outliers)
        outlier_pct = (outlier_count / len(df)) * 100

        if outlier_count > 0:
            entry = {
                "count": int(outlier_count),
                "percentage": float(outlier_pct),
                "lower_bound": float(lower_bound),
                "upper_bound": float(upper_bound),
            }

            # Generate plots for detailed inspection
            plot_path = None
            if plot and plots_done < max_plots:
                fig, axes = plt.subplots(1, 2, figsize=(11, 4))
                fig.suptitle(f"Outliers in {col}: {outlier_count} ({outlier_pct:.2f}%)")

                # Boxplot with bounds
                sns.boxplot(x=df[col], ax=axes[0], color="#69b3a2")
                axes[0].axvline(lower_bound, color="red", linestyle="--", linewidth=1, label="Lower bound")
                axes[0].axvline(upper_bound, color="red", linestyle="--", linewidth=1, label="Upper bound")
                axes[0].set_title(f"Boxplot: {col}")
                axes[0].legend(loc="best")

                # Histogram/KDE with bounds
                sns.histplot(df[col], kde=True, ax=axes[1], color="#4c72b0")
                axes[1].axvline(lower_bound, color="red", linestyle="--", linewidth=1)
                axes[1].axvline(upper_bound, color="red", linestyle="--", linewidth=1)
                axes[1].set_title(f"Distribution: {col}")

                plt.tight_layout()
                if save_dir:
                    safe_col = str(col).replace("/", "_")
                    plot_path = os.path.join(save_dir, f"{safe_col}.png")
                    fig.savefig(plot_path, dpi=150)
                if show:
                    plt.show()
                plt.close(fig)
                plots_done += 1

            if plot_path:
                entry["plot_path"] = plot_path

            outlier_summary[col] = entry

    return outlier_summary

start_time_outliers = now()
outliers_report = detect_outliers_iqr(df)
print(f"Features with outliers: {len(outliers_report)}")
for col, stats in outliers_report.items():
    print(f"  {col}: {stats['count']} outliers ({stats['percentage']:.2f}%)")
end_time_outliers = now()

# Activity: Detect outliers
check_outliers_uuid_executor = "d0e1f2a3-b4c5-4d6e-7f8a-9b0c1d2e3f4a"
check_outliers_uuid_writer = "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b"

check_outliers_activity = [
    ':check_outliers rdf:type prov:Activity .',
    ':check_outliers sc:isPartOf :data_analysis_phase .',
    ':check_outliers rdfs:comment "Detect outliers using IQR method" .',
    ':check_outliers rdfs:comment "Apply IQR-based outlier detection to identify anomalous values that may affect SOM training." .',
    f':check_outliers prov:startedAtTime "{start_time_outliers}"^^xsd:dateTime .',
    f':check_outliers prov:endedAtTime "{end_time_outliers}"^^xsd:dateTime .',
    f':check_outliers prov:qualifiedAssociation :{check_outliers_uuid_executor} .',
    f':{check_outliers_uuid_executor} prov:agent :{executed_by} .',
    f':{check_outliers_uuid_executor} rdf:type prov:Association .',
    f':{check_outliers_uuid_executor} prov:hadRole :{code_executor_role} .',
    f':check_outliers prov:qualifiedAssociation :{check_outliers_uuid_writer} .',
    f':{check_outliers_uuid_writer} prov:agent :{student_a} .',
    f':{check_outliers_uuid_writer} rdf:type prov:Association .',
    f':{check_outliers_uuid_writer} prov:hadRole :{code_writer_role} .',
    ':check_outliers prov:used :raw_data .',
    ':outliers_report rdf:type prov:Entity .',
    f':outliers_report rdfs:comment "Detected outliers in {len(outliers_report)} features using IQR method" .',
    ':outliers_report prov:wasGeneratedBy :check_outliers .',
]
all_provenance_triples.extend(check_outliers_activity)

# Inspect outliers
insp_outliers_uuid_executor = "f2a3b4c5-d6e7-4f8a-9b0c-1d2e3f4a5b6c"

outlier_interpretation = "Outliers detected in several features. For credit risk data, these may represent legitimate extreme cases (e.g., very high credit amounts, long durations). SOMs are relatively robust to outliers as they perform vector quantization. Decision: Keep outliers as they may represent important edge cases in credit assessment."

inspect_outliers_activity = [
    ':inspect_outliers rdf:type prov:Activity .',
    ':inspect_outliers rdfs:comment "Inspect outlier detection results" .',
    f':inspect_outliers rdfs:comment "{outlier_interpretation}" .',
    f':inspect_outliers prov:startedAtTime "{start_time_outliers}"^^xsd:dateTime .',
    f':inspect_outliers prov:endedAtTime "{end_time_outliers}"^^xsd:dateTime .',
    f':inspect_outliers prov:qualifiedAssociation :{insp_outliers_uuid_executor} .',
    f':{insp_outliers_uuid_executor} prov:agent :{student_a} .',
    f':{insp_outliers_uuid_executor} rdf:type prov:Association .',
    f':{insp_outliers_uuid_executor} prov:hadRole :{code_executor_role} .',
    ':inspect_outliers prov:used :outliers_report .',
    ':decision_keep_outliers rdf:type prov:Entity .',
    ':decision_keep_outliers rdfs:comment "Decision: Retain outliers as they may represent valid extreme cases in credit risk assessment" .',
    ':decision_keep_outliers prov:wasGeneratedBy :inspect_outliers .',
]
all_provenance_triples.extend(inspect_outliers_activity)

#############################################
# 6) CORRELATION ANALYSIS
#############################################
print("\n" + "=" * 80)
print("6. CORRELATION ANALYSIS")
print("=" * 80)

def analyze_correlations(df):
    """Analyze correlations between numerical features"""
    numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    if len(numerical_cols) > 1:
        corr_matrix = df[numerical_cols].corr()
        
        # Find high correlations
        high_corr = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                if abs(corr_value) > 0.5:
                    high_corr.append({
                        'feature1': corr_matrix.columns[i],
                        'feature2': corr_matrix.columns[j],
                        'correlation': float(corr_value)
                    })
        
        return {
            "high_correlations": high_corr,
            "correlation_count": len(high_corr)
        }
    else:
        return {"high_correlations": [], "correlation_count": 0}

start_time_corr = now()
corr_report = analyze_correlations(df)
print(f"High correlations (|r| > 0.5): {corr_report['correlation_count']}")
for corr in corr_report['high_correlations']:
    print(f"  {corr['feature1']} <-> {corr['feature2']}: r={corr['correlation']:.3f}")
end_time_corr = now()

# Activity: Analyze correlations
check_corr_uuid_executor = "a3b4c5d6-e7f8-4a9b-0c1d-2e3f4a5b6c7d"
check_corr_uuid_writer = "b4c5d6e7-f8a9-4b0c-1d2e-3f4a5b6c7d8e"

check_corr_activity = [
    ':check_correlations rdf:type prov:Activity .',
    ':check_correlations sc:isPartOf :data_analysis_phase .',
    ':check_correlations rdfs:comment "Analyze feature correlations" .',
    ':check_correlations rdfs:comment "Compute pairwise correlations between numerical features to identify redundant or highly related features." .',
    f':check_correlations prov:startedAtTime "{start_time_corr}"^^xsd:dateTime .',
    f':check_correlations prov:endedAtTime "{end_time_corr}"^^xsd:dateTime .',
    f':check_correlations prov:qualifiedAssociation :{check_corr_uuid_executor} .',
    f':{check_corr_uuid_executor} prov:agent :{executed_by} .',
    f':{check_corr_uuid_executor} rdf:type prov:Association .',
    f':{check_corr_uuid_executor} prov:hadRole :{code_executor_role} .',
    f':check_correlations prov:qualifiedAssociation :{check_corr_uuid_writer} .',
    f':{check_corr_uuid_writer} prov:agent :{student_a} .',
    f':{check_corr_uuid_writer} rdf:type prov:Association .',
    f':{check_corr_uuid_writer} prov:hadRole :{code_writer_role} .',
    ':check_correlations prov:used :raw_data .',
    ':correlations_report rdf:type prov:Entity .',
    f':correlations_report rdfs:comment "Found {corr_report["correlation_count"]} high correlations (|r| > 0.5) between numerical features" .',
    ':correlations_report prov:wasGeneratedBy :check_correlations .',
]
all_provenance_triples.extend(check_corr_activity)

# Inspect correlations
insp_corr_uuid_executor = "c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f"

corr_interpretation = f"Found {corr_report['correlation_count']} high correlations. For SOM analysis, we retain all features as SOMs can handle correlated features and the visualization may reveal interesting relationships. Feature reduction would be considered only if computational constraints arise."

inspect_corr_activity = [
    ':inspect_correlations rdf:type prov:Activity .',
    ':inspect_correlations rdfs:comment "Inspect correlation analysis results" .',
    f':inspect_correlations rdfs:comment "{corr_interpretation}" .',
    f':inspect_correlations prov:startedAtTime "{start_time_corr}"^^xsd:dateTime .',
    f':inspect_correlations prov:endedAtTime "{end_time_corr}"^^xsd:dateTime .',
    f':inspect_correlations prov:qualifiedAssociation :{insp_corr_uuid_executor} .',
    f':{insp_corr_uuid_executor} prov:agent :{student_a} .',
    f':{insp_corr_uuid_executor} rdf:type prov:Association .',
    f':{insp_corr_uuid_executor} prov:hadRole :{code_executor_role} .',
    ':inspect_correlations prov:used :correlations_report .',
    ':decision_keep_all_features rdf:type prov:Entity .',
    ':decision_keep_all_features rdfs:comment "Decision: Retain all features for SOM training as SOMs can visualize feature relationships effectively" .',
    ':decision_keep_all_features prov:wasGeneratedBy :inspect_correlations .',
]
all_provenance_triples.extend(inspect_corr_activity)

#############################################
# 7) CLASS DISTRIBUTION ANALYSIS
#############################################
print("\n" + "=" * 80)
print("7. CLASS DISTRIBUTION ANALYSIS")
print("=" * 80)

def analyze_class_distribution(df):
    """Analyze target class distribution"""
    if 'class' in df.columns:
        class_counts = df['class'].value_counts()
        class_pcts = (class_counts / len(df)) * 100
        imbalance_ratio = class_counts.max() / class_counts.min()
        
        return {
            "classes": {cls: int(count) for cls, count in class_counts.items()},
            "percentages": {cls: float(pct) for cls, pct in class_pcts.items()},
            "imbalance_ratio": float(imbalance_ratio),
            "is_imbalanced": bool(imbalance_ratio > 1.5)
        }
    return None

start_time_class = now()
class_report = analyze_class_distribution(df)
if class_report:
    print(f"Class distribution:")
    for cls, count in class_report['classes'].items():
        print(f"  {cls}: {count} ({class_report['percentages'][cls]:.1f}%)")
    print(f"Imbalance ratio: {class_report['imbalance_ratio']:.2f}:1")
end_time_class = now()

# Activity: Analyze class distribution
check_class_uuid_executor = "d6e7f8a9-b0c1-4d2e-3f4a-5b6c7d8e9f0a"
check_class_uuid_writer = "e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b"

check_class_activity = [
    ':check_class_distribution rdf:type prov:Activity .',
    ':check_class_distribution sc:isPartOf :data_analysis_phase .',
    ':check_class_distribution rdfs:comment "Analyze target class distribution" .',
    ':check_class_distribution rdfs:comment "Examine the balance between good and bad credit risk classes to identify potential class imbalance issues." .',
    f':check_class_distribution prov:startedAtTime "{start_time_class}"^^xsd:dateTime .',
    f':check_class_distribution prov:endedAtTime "{end_time_class}"^^xsd:dateTime .',
    f':check_class_distribution prov:qualifiedAssociation :{check_class_uuid_executor} .',
    f':{check_class_uuid_executor} prov:agent :{executed_by} .',
    f':{check_class_uuid_executor} rdf:type prov:Association .',
    f':{check_class_uuid_executor} prov:hadRole :{code_executor_role} .',
    f':check_class_distribution prov:qualifiedAssociation :{check_class_uuid_writer} .',
    f':{check_class_uuid_writer} prov:agent :{student_a} .',
    f':{check_class_uuid_writer} rdf:type prov:Association .',
    f':{check_class_uuid_writer} prov:hadRole :{code_writer_role} .',
    ':check_class_distribution prov:used :raw_data .',
    ':class_distribution_report rdf:type prov:Entity .',
    f':class_distribution_report rdfs:comment "Class imbalance ratio: {class_report["imbalance_ratio"]:.2f}:1" .',
    ':class_distribution_report prov:wasGeneratedBy :check_class_distribution .',
]
all_provenance_triples.extend(check_class_activity)

# Inspect class distribution
insp_class_uuid_executor = "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c"

class_interpretation = f"Dataset shows class imbalance with ratio {class_report['imbalance_ratio']:.2f}:1. The majority class (good credit) represents about {max(class_report['percentages'].values()):.1f}% of samples. For SOM analysis, this imbalance will be visible in class distribution visualizations and may affect cluster purity."

inspect_class_activity = [
    ':inspect_class_distribution rdf:type prov:Activity .',
    ':inspect_class_distribution rdfs:comment "Inspect class distribution" .',
    f':inspect_class_distribution rdfs:comment "{class_interpretation}" .',
    f':inspect_class_distribution prov:startedAtTime "{start_time_class}"^^xsd:dateTime .',
    f':inspect_class_distribution prov:endedAtTime "{end_time_class}"^^xsd:dateTime .',
    f':inspect_class_distribution prov:qualifiedAssociation :{insp_class_uuid_executor} .',
    f':{insp_class_uuid_executor} prov:agent :{student_a} .',
    f':{insp_class_uuid_executor} rdf:type prov:Association .',
    f':{insp_class_uuid_executor} prov:hadRole :{code_executor_role} .',
    ':inspect_class_distribution prov:used :class_distribution_report .',
    ':hypothesis_cluster_structure rdf:type prov:Entity .',
    ':hypothesis_cluster_structure rdfs:comment "Hypothesis: Expect to see majority class dominating most SOM units with minority class potentially forming smaller, more concentrated clusters. Class overlap may indicate inherent difficulty in credit risk prediction." .',
    ':hypothesis_cluster_structure prov:wasGeneratedBy :inspect_class_distribution .',
]
all_provenance_triples.extend(inspect_class_activity)

#############################################
# 8) HYPOTHESES (Added as simple PROV-O comments)
#############################################
print("\n" + "=" * 80)
print("8. HYPOTHESES (for SOM exploration)")
print("=" * 80)

# Compute lightweight summaries to ground hypotheses
numerical_cols = df.select_dtypes(include=[np.number]).columns.tolist()
skew_vals = df[numerical_cols].skew(numeric_only=True)
right_skewed = [col for col, v in skew_vals.items() if v > 0.5]
left_skewed = [col for col, v in skew_vals.items() if v < -0.5]

distribution_hypothesis_parts = []
if right_skewed:
    distribution_hypothesis_parts.append(
        f"Right-skew likely in {', '.join(right_skewed[:5])}{' and others' if len(right_skewed) > 5 else ''}."
    )
if left_skewed:
    distribution_hypothesis_parts.append(
        f"Left-skew present in {', '.join(left_skewed[:5])}{' and others' if len(left_skewed) > 5 else ''}."
    )
if outliers_report and len(outliers_report) > 0:
    distribution_hypothesis_parts.append(
        f"IQR flagged outliers in {len(outliers_report)} features; expect long tails with valid extreme cases."
    )
if not distribution_hypothesis_parts:
    distribution_hypothesis_parts.append("Distributions appear fairly symmetric with moderate variance across features.")
distribution_hypothesis = " ".join(distribution_hypothesis_parts)

# Cluster count and relationships hypothesis
cluster_rel_hypothesis = (
    "Given heterogeneous scales and detected correlations, expect ~3–6 clusters "
    "structured around credit amount, duration, and age. Correlated features may "
    "yield elongated clusters along shared axes with gradual transitions rather than sharp boundaries."
)
if corr_report and corr_report.get("correlation_count", 0) > 0:
    cluster_rel_hypothesis += f" Observed {corr_report['correlation_count']} moderately/highly correlated pairs (|r| > 0.5)."

# Majority/minority classes hypothesis
if class_report:
    maj_pct = max(class_report['percentages'].values())
    min_pct = min(class_report['percentages'].values())
    class_balance_hypothesis = (
        f"Class imbalance likely manifests as majority-class dominance across most SOM units "
        f"(~{maj_pct:.1f}% vs. ~{min_pct:.1f}%). Minority class may form smaller, more concentrated regions "
        "and overlap with majority in mixed units."
    )
else:
    class_balance_hypothesis = (
        "Class labels unavailable; cluster composition will be inferred solely from feature distributions."
    )

# Print hypotheses to console
print("- Data distribution:")
print(f"  {distribution_hypothesis}")
print("- Cluster structure:")
print(f"  {cluster_rel_hypothesis}")
print("- Majority/minority:")
print(f"  {class_balance_hypothesis}")

# Record hypotheses in PROV-O as simple comments
hyp_start = now()
hyp_end = now()
hypotheses_activity = [
    ':formulate_hypotheses rdf:type prov:Activity .',
    ':formulate_hypotheses sc:isPartOf :data_analysis_phase .',
    ':formulate_hypotheses rdfs:label "Formulate Hypotheses" .',
    ':formulate_hypotheses rdfs:comment "High-level hypotheses to guide SOM exploration" .',
    f':formulate_hypotheses prov:startedAtTime "{hyp_start}"^^xsd:dateTime .',
    f':formulate_hypotheses prov:endedAtTime "{hyp_end}"^^xsd:dateTime .',
    ':formulate_hypotheses prov:used :value_ranges_report .',
    ':formulate_hypotheses prov:used :outliers_report .',
    ':formulate_hypotheses prov:used :correlations_report .',
    ':formulate_hypotheses prov:used :class_distribution_report .',
    ':hypothesis_data_distribution rdf:type prov:Entity .',
    f':hypothesis_data_distribution rdfs:comment "{distribution_hypothesis}" .',
    ':hypothesis_data_distribution prov:wasGeneratedBy :formulate_hypotheses .',
    ':hypothesis_cluster_structure_simple rdf:type prov:Entity .',
    f':hypothesis_cluster_structure_simple rdfs:comment "{cluster_rel_hypothesis}" .',
    ':hypothesis_cluster_structure_simple prov:wasGeneratedBy :formulate_hypotheses .',
    ':hypothesis_class_balance rdf:type prov:Entity .',
    f':hypothesis_class_balance rdfs:comment "{class_balance_hypothesis}" .',
    ':hypothesis_class_balance prov:wasGeneratedBy :formulate_hypotheses .',
]
all_provenance_triples.extend(hypotheses_activity)

#############################################
# SAVE RESULTS
#############################################
print("\n" + "=" * 80)
print("SAVING RESULTS")
print("=" * 80)

# Save all reports to JSON
all_reports = {
    "data_size": data_size_report,
    "attribute_types": attr_types_report,
    "value_ranges": ranges_report,
    "missing_values": missing_report,
    "outliers": outliers_report,
    "correlations": corr_report,
    "class_distribution": class_report
}

with open('data/analysis_reports.json', 'w') as f:
    json.dump(all_reports, f, indent=2)
print("✓ Saved analysis reports to data/analysis_reports.json")

# Save provenance triples
with open('data/analysis_provenance_triples.txt', 'w') as f:
    for triple in all_provenance_triples:
        f.write(triple + '\n')
print(f"✓ Saved {len(all_provenance_triples)} provenance triples to data/analysis_provenance_triples.txt")

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
print(f"\nGenerated {len(all_provenance_triples)} PROV-O triples documenting the analysis workflow")
print("All triples are ready to be inserted into the triple store using engine.insert()")
