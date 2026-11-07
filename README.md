# Regime & Anomaly Unsupervised Analysis

Unsupervised analysis of energy consumption patterns and anomalies in a small-scale steel industry.

## Team

- Alexandre Franco
- Caio Cunha Franco
- Rodrigo Franco

## Project Overview

This project analyzes electricity consumption data from a small-scale steel industry in South Korea. The goal is to explore consumption behavior, detect anomalous energy usage, and identify distinct operational regimes using unsupervised learning techniques.

The dataset was collected from **DAEWOO Steel Co. Ltd**, located in **Gwangyang, South Korea**. The company produces several types of coils, steel plates, and iron plates. Electricity consumption information is maintained in a cloud-based system, while energy consumption data is obtained from the **Korea Electric Power Corporation** website ([pccs.kepco.go.kr](https://pccs.kepco.go.kr)). Daily, monthly, and annual perspectives are calculated and displayed.

## Dataset

- **Source:** [Steel Industry Energy Consumption](https://archive.ics.uci.edu/ml/datasets/Steel+Industry+Energy+Consumption) — UCI Machine Learning Repository
- **Donation date:** August 13, 2023
- **Instances:** 35,040
- **Features:** 9
- **Feature types:** Real and categorical
- **Associated task:** Regression
- **Subject area:** Physics and Chemistry

## Objectives

- Perform exploratory data analysis (EDA) to understand energy consumption patterns.
- Apply unsupervised learning techniques to detect anomalies in energy usage.
- Identify different consumption regimes, such as peak periods and seasonal variations.
- Evaluate the feasibility of regression-based consumption forecasting using the available features.
- Produce clear visualizations and reproducible analysis notebooks.

## Repository Structure

```text
.
├── data/
│   └── steel_industry_energy_consumption.csv  # Original dataset
├── notebooks/
│   ├── 01_exploratory_data_analysis.ipynb    # Exploratory data analysis
│   ├── 02_anomaly_detection.ipynb            # Anomaly detection
│   └── 03_regime_identification.ipynb        # Regime identification
├── src/
│   ├── data_preprocessing.py                 # Preprocessing functions
│   ├── anomaly_detection.py                  # Anomaly detection algorithms
│   └── visualization.py                      # Visualization utilities
├── requirements.txt                          # Project dependencies
└── README.md                                 # Project documentation
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/MBA-Data-Science-Unifor/Regime-Anomaly-Unsupervisioned.git
   cd Regime-Anomaly-Unsupervisioned
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate      # Linux / macOS
   venv\Scripts\activate         # Windows
   ```

3. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Exploratory Data Analysis**  
   Run `notebooks/01_exploratory_data_analysis.ipynb` to inspect distributions, correlations, and temporal consumption trends.

2. **Anomaly Detection**  
   Use `notebooks/02_anomaly_detection.ipynb` to apply anomaly detection methods such as Isolation Forest, Local Outlier Factor (LOF), or Autoencoders.

3. **Regime Identification**  
   Use `notebooks/03_regime_identification.ipynb` to apply clustering techniques such as K-Means or DBSCAN and segment consumption patterns into distinct regimes.

Scripts can also be executed directly:

```bash
python src/data_preprocessing.py --input data/steel_industry_energy_consumption.csv
python src/anomaly_detection.py --method isolation_forest
```

## Expected Results

- Time-series visualizations of energy consumption by hour, day, and month.
- Detection of anomalous consumption peaks and possible contributing factors.
- Clustering of periods with similar consumption behavior, representing different operational regimes.
- Regression models for forecasting consumption based on variables such as load and day of the week.
- Reproducible notebooks and reusable preprocessing, detection, and visualization code.

## Contributing

Contributions are welcome. If you would like to improve the analysis, fix an issue, or add a new method, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **DAEWOO Steel Co. Ltd** for providing the data.
- **Korea Electric Power Corporation** for the energy consumption information.
- **UCI Machine Learning Repository** for hosting the dataset.
- **MBA in Data Science at Unifor** for support and encouragement.

---

This README can be updated as the project evolves and new analyses, methods, or results are added.