# Automated Data Analysis Tool

## Overview
This project provides an automated pipeline for exploratory data analysis (EDA) using Python. It takes a dataset in CSV format as input and generates detailed statistical summaries, visualizations, and insights, all of which are saved to an output directory.

## Features
- **Data Summarization**: Provides key statistics such as mean, standard deviation, missing values, and more for each column.
- **Outlier Detection**: Identifies outliers in numeric columns using the Interquartile Range (IQR) method.
- **Correlation Analysis**: Generates a heatmap to visualize the relationships between numeric variables.
- **Missing Values Visualization**: Highlights missing values using a heatmap.
- **LLM Integration**: Uses OpenAI's GPT-4 to generate insights and narratives from the dataset.
- **Markdown Report**: Outputs a `README.md` summarizing the analysis, including visualizations and generated insights.

## Installation
### Prerequisites
- Python 3.11 or higher
- Required Python libraries:
  - `httpx`
  - `pandas`
  - `numpy`
  - `matplotlib`
  - `seaborn`
  - `tenacity`
  - `openai`

### Setup
1. Clone the repository.
   ```bash
   git clone <repository-url>
   cd <repository-folder>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up the OpenAI API key as an environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key"
   ```

## Usage
To analyze a dataset, run the following command:
```bash
uv run autolysis.py <path-to-dataset.csv>
```
### Example
```bash
uv run autolysis.py data.csv
```
This command will:
1. Analyze `data.csv`.
2. Generate visualizations and save them to the output directory.
3. Generate insights using GPT-4.
4. Create a `README.md` file summarizing the results.

## Output
The analysis output includes:
- `README.md`: A detailed markdown report summarizing the dataset, insights, and visualizations.
- Visualizations:
  - `correlation_heatmap.png`: Heatmap of correlations between numeric columns.
  - `missing_values_heatmap.png`: Heatmap showing missing values in the dataset.

## Project Structure
```
.
├── autolysis.py          # Main script for data analysis
├── requirements.txt      # Python dependencies
├── data.csv              # Example dataset (replace with your own)
├── <dataset-output-dir>/ # Directory containing analysis outputs
│   ├── README.md         # Summary report
│   ├── correlation_heatmap.png
│   ├── missing_values_heatmap.png
```

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License.

