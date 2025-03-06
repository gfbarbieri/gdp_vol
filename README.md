# GDP Volatility Analysis

A Python package for analyzing GDP volatility through a modular pipeline that handles data loading, transformation, and analysis.

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## Features
- **Data Loading**: Support for multiple data sources (CSV, Excel, JSON, YAML, HTTP, APIs)
- **Data Transformation**: Time series transformations including:
  - Log transformations
  - Difference calculations
  - Hodrick-Prescott filtering
  - Linear detrending
- **Metrics**: Statistical and economic indicators
- **Regression Analysis**: Comprehensive regression tools

## Quick Start
```python
from gdp_vol.data_loading import DataRetriever
from gdp_vol.data_transformation import DataTransformer
from gdp_vol.metrics import calculate_volatility
from gdp_vol.regression import run_regression

# Load data
loader = DataRetriever.create("data/gdp.csv")
df = loader.load_data()

# Transform data
transformer = DataTransformer(df, frequency="Q")
transformer.log_transform("gdp", "gdp_log")
transformer.difference("gdp_log", periods=1, new_col_name="gdp_growth")

# Calculate metrics
volatility = calculate_volatility(df["gdp_growth"])

# Run regression
results = run_regression(df, dependent="gdp_growth", independent=["inflation", "interest_rate"])
```

## Documentation
For detailed technical documentation, please see [architecture.md](architecture.md).

## Project Structure
```
src/
├── data_loading/      # Data ingestion and loading
├── data_transformation/# Data preprocessing and transformations
├── metrics/           # Statistical and economic metrics
├── regression/        # Regression analysis
└── main.py           # Main entry point
```

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development Setup
1. Clone the repository
```bash
git clone https://github.com/yourusername/gdp-vol.git
cd gdp-vol
```

2. Install dependencies
```bash
# Using poetry
poetry install

# Using pip
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create requirements.txt file from poetry, if required.
```bash
poetry export -f requirements.txt --output requirements.txt
```

4. Run tests
```bash
pytest tests/
```

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
