# 🎯 Composite Indicator Builder

**Professional tool for constructing composite indicators using various methodologies**

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

**Author:** Dr. Merwan Roudane  
**Email:** merwanroudane920@gmail.com  
**GitHub:** [merwanroudane/indic](https://github.com/merwanroudane/indicators)

---

## 📋 Overview

The **Composite Indicator Builder** is a comprehensive Python package designed for researchers, economists, and data analysts who need to construct composite indicators following OECD guidelines and academic best practices. The package features a beautiful modern GUI built with CustomTkinter and implements multiple weighting and aggregation methodologies.

## ✨ Key Features

- 🎨 **Modern GUI** - Beautiful, intuitive interface with light/dark mode support
- 📊 **Multiple Methods** - 9 different calculation methodologies
- 📈 **Advanced Analytics** - Built-in visualizations and statistical analysis
- 💾 **Excel Integration** - Import data and export results seamlessly
- 🔬 **Research-Grade** - Based on OECD Handbook and peer-reviewed literature
- 🌐 **Cross-Platform** - Works on Windows, macOS, and Linux

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/merwanroudane/indic.git
cd indic

# Install the package
pip install -e .

# Or install directly from GitHub
pip install git+https://github.com/merwanroudane/indic.git
```

### Launch the Application

```bash
# Run from command line
indicator

# Or run from Python
python -m indicator.gui
```

### Basic Usage Example

```python
import pandas as pd
from indicator import PCA_Calculation, EqualWeights, normalizar_dados

# Load your data
df = pd.read_excel("your_data.xlsx")

# Normalize data
data = pd.DataFrame()
for col in df.select_dtypes(include=['number']).columns:
    data[col] = normalizar_dados(df[col].tolist(), orientacao="Min")

# Calculate using PCA
pca_model = PCA_Calculation(data)
results = pca_model.run()

# Access results
for i, result in enumerate(results):
    print(f"Unit {i+1}: CI = {result.ci:.3f}, Weights = {result.weights}")
```

## 📚 Methodology

### Available Methods

1. **Principal Component Analysis (PCA)**
   - Statistical method based on variance explained
   - Includes Varimax rotation for interpretability
   - Filters components using OECD criteria

2. **Shannon's Entropy**
   - Information theory-based weighting
   - Assigns higher weights to discriminatory indicators
   - Fully data-driven approach

3. **Benefit of the Doubt (BoD)**
   - Based on Data Envelopment Analysis (DEA)
   - Optimizes weights to maximize each unit's performance
   - Can incorporate expert opinion through bounds

4. **Equal Weights**
   - Simple arithmetic mean
   - Baseline method for comparison
   - Assumes equal importance of all indicators

5. **Geometric Mean**
   - Multiplicative aggregation
   - Less compensatory than arithmetic mean
   - Suitable for essential indicators

6. **Harmonic Mean**
   - Least compensatory aggregation
   - Penalizes poor performance
   - Ideal for critical dimensions

7. **Factor Analysis**
   - Assumes underlying latent factors
   - Alternative to PCA
   - Includes Varimax rotation

8. **Correlation-based Weighting**
   - Weights based on correlation structure
   - Simple and interpretable
   - Can use reference indicator

9. **Minimal Uncertainty**
   - Optimizes to minimize ranking uncertainty
   - Combines information from multiple methods
   - Provides robust consensus ranking

## 🎨 GUI Features

### Main Interface

The application features a modern, professional interface with:

- **Sidebar Controls** - Easy access to all settings and options
- **Data Preview** - View your imported data
- **Interactive Results** - Explore results with tabs for each method
- **Visualizations** - Automatic generation of charts and graphs
- **Export Functionality** - One-click Excel export

### Screenshots

```
┌─────────────────────────────────────────────────────────────┐
│  🔬 Indicator Builder          Dr. Merwan Roudane          │
├──────────────┬──────────────────────────────────────────────┤
│              │                                              │
│  📁 Data     │         📋 Data Preview                      │
│  Management  │                                              │
│              │    ┌──────────────────────────────────┐     │
│  📊 Select   │    │  DMU  │  Ind1  │  Ind2  │  Ind3 │     │
│  Indicators  │    ├────────────────────────────────  │     │
│              │    │   1   │  0.75  │  0.82  │  0.91 │     │
│  ⚙️ Methods   │    │   2   │  0.63  │  0.77  │  0.85 │     │
│              │    │  ...  │  ...   │  ...   │  ...  │     │
│  🚀 Calculate│    └──────────────────────────────────┘     │
│              │                                              │
│  💾 Export   │         📊 Results & Visualizations         │
│              │                                              │
└──────────────┴──────────────────────────────────────────────┘
```

## 📖 User Guide

### 1. Loading Data

- Click **"Load Excel File"**
- Select your Excel file (.xlsx or .xls)
- Data should have:
  - Numeric columns for indicators
  - Optional label column for unit names
  - No missing values

### 2. Selecting Indicators

- Check boxes next to indicators you want to include
- Choose a **Label Column** (optional) for unit identification
- Select a **Control Variable** (optional) for normalization

### 3. Choosing Methods

- Select one or more calculation methods
- Different methods provide different perspectives
- Use multiple methods for robustness analysis

### 4. Calculating

- Click **"Calculate Indicators"**
- Progress bar shows calculation status
- Results appear in separate tabs

### 5. Reviewing Results

Each result tab shows:
- **Rankings** - Sorted composite indicator values
- **Weights** - Indicator weights used
- **Statistics** - Min, max, mean, standard deviation
- **Visualizations** - Bar charts and distributions

### 6. Exporting

- Click **"Export Results"**
- Choose save location
- Excel file contains:
  - Separate sheets for each method
  - Summary statistics sheet
  - Full weight information

## 💻 Python API

### Basic Example

```python
from indicator import PCA_Calculation, normalizar_dados
import pandas as pd

# Load and prepare data
df = pd.read_excel("data.xlsx")
data = pd.DataFrame({
    col: normalizar_dados(df[col].tolist(), "Min")
    for col in df.select_dtypes(include=['number']).columns
})

# Calculate composite indicators
model = PCA_Calculation(data)
results = model.run()

# Extract CI values and weights
ci_values = [r.ci for r in results]
weights = results[0].weights  # Same for all units in PCA
```

### Advanced Usage - Multiple Methods

```python
from indicator import (
    PCA_Calculation, 
    Entropy_Calculation, 
    BOD_Calculation,
    GeometricMean
)

methods = {
    'PCA': PCA_Calculation(data),
    'Entropy': Entropy_Calculation(data),
    'BoD': BOD_Calculation(data),
    'Geometric': GeometricMean(data)
}

results = {}
for name, model in methods.items():
    results[name] = model.run()
    
# Compare results across methods
import numpy as np
correlations = {}
for m1 in results:
    for m2 in results:
        if m1 < m2:
            ci1 = [r.ci for r in results[m1]]
            ci2 = [r.ci for r in results[m2]]
            corr = np.corrcoef(ci1, ci2)[0, 1]
            correlations[f"{m1} vs {m2}"] = corr
```

### Custom Bounds for BoD

```python
from indicator import BOD_Calculation

# Set min/max bounds for each indicator
bounds = [
    (0.1, 0.5),  # Indicator 1: weight between 0.1 and 0.5
    (0.0, 0.3),  # Indicator 2: weight between 0.0 and 0.3
    (0.2, 0.8),  # Indicator 3: weight between 0.2 and 0.8
]

model = BOD_Calculation(data, bounds=bounds)
results = model.run()
```

## 📊 Data Requirements

### Input Format

- **File Type:** Excel (.xlsx, .xls)
- **Structure:** 
  - Rows = Units/Entities (DMUs, countries, regions, etc.)
  - Columns = Indicators + optional label column
- **Data Type:** Numeric values for indicators
- **Missing Data:** Not allowed (will prompt error)
- **Size:** Recommended maximum 300 rows

### Example Data Structure

| Country | GDP_per_capita | Life_Expectancy | Education_Index |
|---------|----------------|-----------------|-----------------|
| USA     | 65000          | 78.5            | 0.92            |
| Germany | 48000          | 81.0            | 0.95            |
| Japan   | 42000          | 84.5            | 0.94            |

## 🔬 Scientific Background

### Normalization

The package implements Min-Max normalization:

- **Min-oriented:** (x - min) / (max - min) → Higher values are better
- **Max-oriented:** (max - x) / (max - min) → Lower values are better

Orientation is automatically determined by correlation with control variable.

### Weight Determination

Different methods use different approaches:

- **PCA/Factor Analysis:** Based on variance explained
- **Entropy:** Based on information content
- **BoD:** Based on linear programming
- **Correlation:** Based on correlation structure

### Aggregation

Multiple aggregation functions:

- **Linear:** Weighted arithmetic mean (fully compensatory)
- **Geometric:** Multiplicative (partially compensatory)
- **Harmonic:** Least compensatory

## 📚 References

### Key Literature

1. **OECD (2008)**. *Handbook on Constructing Composite Indicators: Methodology and User Guide*. OECD Publishing, Paris.

2. **Nardo, M., et al. (2005)**. *Handbook on Constructing Composite Indicators*. OECD Statistics Working Papers.

3. **Cherchye, L., et al. (2007)**. "An Introduction to 'Benefit of the Doubt' Composite Indicators." *Social Indicators Research*, 82(1), 111-145.

4. **Zhou, P., Ang, B.W., & Poh, K.L. (2007)**. "A non-radial DEA approach to measuring environmental performance." *European Journal of Operational Research*, 178(1), 1-9.

5. **Greco, S., et al. (2019)**. "On the Methodological Framework of Composite Indices: A Review." *Social Indicators Research*, 141, 61-94.

## 🛠️ Development

### Requirements

```bash
pip install -r requirements.txt
```

### Testing

```bash
pytest tests/
```

### Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Dr. Merwan Roudane**

- Email: merwanroudane920@gmail.com
- GitHub: [@merwanroudane](https://github.com/merwanroudane)
- Repository: [merwanroudane/indic](https://github.com/merwanroudane/indic)

## 🙏 Acknowledgments

- OECD for methodological guidelines
- Academic community for research foundations
- Open-source community for excellent tools and libraries

## 📞 Support

For questions, issues, or suggestions:

- **Email:** merwanroudane920@gmail.com
- **Issues:** [GitHub Issues](https://github.com/merwanroudane/indic/issues)

## 📈 Citation

If you use this package in your research, please cite:

```bibtex
@software{roudane2024indicator,
  author = {Roudane, Merwan},
  title = {Composite Indicator Builder: A Python Package for Constructing Composite Indicators},
  year = {2024},
  url = {https://github.com/merwanroudane/indic},
  version = {1.0.0}
}
```

---

**Made with ❤️ by Dr. Merwan Roudane**
