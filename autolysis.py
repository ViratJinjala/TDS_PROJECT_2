import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
import numpy as np
import chardet
import requests
import sys
import argparse

# Configuration for LLM API Proxy
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")
if not AIPROXY_TOKEN:
    print("Error: AIPROXY_TOKEN environment variable is not set.")
    sys.exit(1)

CONFIG = {
    "AI_PROXY_URL": "https://aiproxy.sanand.workers.dev/openai/v1/chat/completions", 
    "AIPROXY_TOKEN": AIPROXY_TOKEN,
    "OUTPUT_DIR": os.getcwd()
}

# Function to interact with LLM via AI Proxy
def ask_llm(question, context):
    try:
        headers = {"Authorization": f"Bearer {CONFIG['AIPROXY_TOKEN']}", "Content-Type": "application/json"}
        payload = {
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": f"{question}\nContext:\n{context}"}]
        }
        response = requests.post(CONFIG["AI_PROXY_URL"], headers=headers, json=payload)
        response.raise_for_status()
        response_json = response.json()
        return response_json['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with AI Proxy: {e}")
        sys.exit(1)

# Function to save visualizations
def visualization(plt, file_name):
    try:
        plt.tight_layout()
        save_path = os.path.join(CONFIG["OUTPUT_DIR"], file_name)
        print(f"Saving visualization to: {save_path}")
        plt.savefig(save_path, bbox_inches='tight')
        plt.close()
    except Exception as e:
        print(f"Error saving visualization {file_name}: {e}")

# Function to detect encoding
def detect_encoding(file_path):
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
        result = chardet.detect(raw_data)
        return result['encoding']
    except Exception as e:
        print(f"Error detecting file encoding: {e}")
        sys.exit(1)

# Function to perform missing data analysis
def analyze_missing_data(df):
    missing_data = df.isnull().sum()
    missing_percent = (missing_data / len(df)) * 100
    missing_summary = missing_percent[missing_percent > 0].sort_values(ascending=False)
    plt.figure(figsize=(10, 6))
    missing_summary.plot(kind='bar', color='skyblue')
    plt.title("Percentage of Missing Data by Column")
    plt.ylabel("Percentage")
    visualization(plt, "missing_data.png")  
    return missing_summary

# Function to perform correlation analysis
def analyze_correlation(df):
    numeric_df = df.select_dtypes(include=[np.number])
    if not numeric_df.empty:
        correlation_matrix = numeric_df.corr()
        plt.figure(figsize=(10, 6))
        sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
        plt.title("Correlation Heatmap")
        visualization(plt, "correlation_heatmap.png")
        return correlation_matrix
    return None

# Function to detect outliers
def detect_outliers(df):
    numerical_cols = df.select_dtypes(include=[np.number])
    outlier_summary = {}
    for col in numerical_cols.columns:
        q1 = numerical_cols[col].quantile(0.25)
        q3 = numerical_cols[col].quantile(0.75)
        iqr = q3 - q1
        outliers = numerical_cols[(numerical_cols[col] < (q1 - 1.5 * iqr)) | (numerical_cols[col] > (q3 + 1.5 * iqr))]
        outlier_summary[col] = len(outliers)
    return outlier_summary

# Function to perform clustering analysis
def perform_clustering(df):
    numerical_cols = df.select_dtypes(include=[np.number])
    if not numerical_cols.empty:
        kmeans = KMeans(n_clusters=3, random_state=42)
        df['Cluster'] = kmeans.fit_predict(numerical_cols.fillna(0))
        plt.figure(figsize=(10, 6))
        sns.scatterplot(x=numerical_cols.columns[0], y=numerical_cols.columns[1], hue='Cluster', data=df, palette='viridis')
        plt.title("Cluster Visualization")
        visualization(plt, "clusters.png")        
        return df['Cluster'].value_counts()
    return None

# Function to analyze distribution of numerical columns
def analyze_distribution(df):
    numerical_cols = df.select_dtypes(include=[np.number])
    for col in numerical_cols.columns:
        plt.figure(figsize=(10, 6))
        sns.histplot(df[col], kde=True, bins=30, color="blue")
        plt.title(f"Distribution of {col}")
        plt.xlabel(col)
        plt.ylabel("Frequency")
        visualization(plt, f"{col}_distribution.png")

# Function to generate the README file using LLM
def generate_readme(df, missing_summary, correlation_matrix, outlier_summary, clustering_summary):
    analysis_context = f"""
    Data Overview:
    The dataset contains {df.shape[0]} rows and {df.shape[1]} columns. It includes the following columns: {', '.join(df.columns)}.

    Missing Data:
    {missing_summary}

    Correlation Matrix:
    {correlation_matrix}

    Outliers Detected:
    {outlier_summary}

    Clustering Summary:
    {clustering_summary}
    """

    story = ask_llm("Write a story based on the dataset analysis, including key findings and implications.", analysis_context)
    dynamic_analysis = ask_llm("Based on the findings so far, suggest any further analysis or insights that should be explored.", analysis_context)
    
    readme_path = os.path.join(CONFIG["OUTPUT_DIR"], "README.md")
    print(f"Saving README.md to: {readme_path}")
    try:
        with open(readme_path, "w") as f:
            f.write("# Data Analysis Report\n\n")
            f.write(f"## Data Overview\n\n")
            f.write(f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns. It includes the following columns: {', '.join(df.columns)}.\n\n")
            f.write("## Missing Data\n")
            f.write(f"{missing_summary}\n\n")
            f.write("## Correlation Matrix\n")
            f.write(f"{correlation_matrix}\n\n")
            f.write("## Outliers\n")
            f.write(f"{outlier_summary}\n\n")
            f.write("## Clustering\n")
            f.write(f"{clustering_summary}\n\n")
            f.write("## Dynamic Insights\n")
            f.write(f"{dynamic_analysis}\n\n")
            f.write("## Story-based Summary\n")
            f.write(story)
        print("README.md file created successfully.")
    except Exception as e:
        print(f"Error creating README.md file: {e}")

# Main function to analyze the dataset and generate the report
def get_dataset_file():
    if len(sys.argv) != 2:
        print("Usage: uv run autolysis.py <dataset.csv>")
        sys.exit(1)

    file_path = sys.argv[1]
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        sys.exit(1)
    
    return file_path

# Main function to analyze the dataset and generate the report
def analyze_data(file_path):
    encoding = detect_encoding(file_path)
    df = pd.read_csv(file_path, encoding=encoding)
    print(f"Loaded dataset {file_path} with {df.shape[0]} rows and {df.shape[1]} columns.")
    missing_summary = analyze_missing_data(df)
    correlation_matrix = analyze_correlation(df)
    outlier_summary = detect_outliers(df)
    clustering_summary = perform_clustering(df)
    analyze_distribution(df)
    generate_readme(df, missing_summary, correlation_matrix, outlier_summary, clustering_summary)

# Entry point
if __name__ == "__main__":
    dataset_file = get_dataset_file()
    analyze_data(dataset_file)