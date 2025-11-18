# 📖 User Manual - Composite Indicator Builder

**Version 1.0.0**  
**Author: Dr. Merwan Roudane**  
**Email: merwanroudane920@gmail.com**

---

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [User Interface Guide](#user-interface-guide)
5. [Methodology](#methodology)
6. [Data Preparation](#data-preparation)
7. [Workflow](#workflow)
8. [Methods Explained](#methods-explained)
9. [Interpreting Results](#interpreting-results)
10. [Advanced Features](#advanced-features)
11. [Troubleshooting](#troubleshooting)
12. [FAQ](#faq)

---

## 1. Introduction

The Composite Indicator Builder is a professional tool designed for researchers, economists, and analysts who need to construct composite indicators. The application implements methodologies from the OECD Handbook and academic literature, providing a rigorous yet user-friendly approach to indicator construction.

### Key Features
- 9 different calculation methods
- Modern, intuitive GUI
- Automatic data normalization
- Interactive visualizations
- Excel import/export
- Comprehensive statistical analysis

---

## 2. Installation

### System Requirements
- **Operating System:** Windows 7+, macOS 10.12+, or Linux
- **Python:** Version 3.8 or higher
- **RAM:** 4 GB minimum, 8 GB recommended
- **Disk Space:** 500 MB

### Installation Steps

#### Option 1: Using pip
```bash
pip install indicator
```

#### Option 2: From source
```bash
git clone https://github.com/merwanroudane/indic.git
cd indic
pip install -e .
```

#### Option 3: Using launcher scripts
- **Windows:** Double-click `launch.bat`
- **Mac/Linux:** Run `./launch.sh`

---

## 3. Getting Started

### First Launch

1. Start the application:
   ```bash
   indicator
   ```

2. The welcome screen will appear with:
   - Feature overview
   - Available methods
   - Quick instructions

### Sample Data

Try the application with provided sample data:
```bash
cd examples
python generate_sample_data.py
```

This creates `sample_data.xlsx` with 30 countries and 10 indicators.

---

## 4. User Interface Guide

### Layout

The application window is divided into two main areas:

#### Sidebar (Left)
- **Header:** Application name and author
- **Data Management:** Load Excel files
- **Indicator Selection:** Choose indicators to include
- **Label Column:** Select identifier column
- **Control Variable:** Choose reference for normalization
- **Methods:** Select calculation methods
- **Calculate Button:** Run calculations
- **Export Button:** Save results

#### Main Area (Right)
- **Data Preview Tab:** View loaded data
- **Results Tabs:** One tab per selected method
- **Visualizations:** Charts and graphs
- **Statistics:** Summary statistics

### Color Scheme

The application uses a professional color palette:
- **Primary Blue:** Main actions and headers
- **Success Green:** Positive actions (load, export)
- **Info Cyan:** Information and documentation
- **Warm Orange:** Highlights and accents

---

## 5. Methodology

### Theoretical Framework

Composite indicators combine multiple individual indicators into a single index. The construction process involves:

1. **Data Selection:** Choose relevant indicators
2. **Normalization:** Make indicators comparable
3. **Weighting:** Assign importance to indicators
4. **Aggregation:** Combine into single value

### OECD Guidelines

The application follows OECD recommendations:
- Transparent methodology
- Robustness analysis
- Sensitivity testing
- Clear documentation
- Proper visualization

---

## 6. Data Preparation

### Excel File Structure

Your Excel file should have:

**Columns:**
- One column for labels/identifiers (optional)
- Multiple columns for numeric indicators

**Rows:**
- Each row = one unit (country, company, region, etc.)
- No missing values allowed
- Maximum 300 rows recommended

### Example Structure

| Country | GDP | Education | Health | Environment |
|---------|-----|-----------|--------|-------------|
| USA     | 65  | 0.92      | 78.5   | 75.0        |
| Germany | 48  | 0.95      | 81.0   | 70.0        |
| Japan   | 42  | 0.94      | 84.5   | 80.0        |

### Data Quality

Ensure your data:
- ✅ Is numeric (except label column)
- ✅ Has no missing values
- ✅ Has consistent units
- ✅ Is properly formatted
- ✅ Represents comparable concepts

---

## 7. Workflow

### Step-by-Step Process

#### Step 1: Load Data
1. Click **"Load Excel File"**
2. Select your file
3. Review any warnings about missing data
4. Check data preview

#### Step 2: Select Indicators
1. Check boxes next to indicators to include
2. Minimum: 1 indicator
3. Recommended: 3-10 indicators
4. Too many indicators may cause issues

#### Step 3: Configure Options

**Label Column:**
- Select column for unit names
- Leave as "None" to auto-generate (DMU 1, DMU 2, etc.)

**Control Variable:**
- Optional reference indicator
- Used to determine normalization direction
- If correlation > 0: Min-oriented
- If correlation < 0: Max-oriented
- Leave as "None" for default (Min-oriented)

#### Step 4: Choose Methods
Select one or more methods:
- Start with 2-3 methods for comparison
- Use all methods for comprehensive analysis
- Some methods require others (e.g., Minimal Uncertainty)

#### Step 5: Calculate
1. Click **"Calculate Indicators"**
2. Progress bar shows status
3. Wait for completion (usually < 30 seconds)

#### Step 6: Review Results
- Switch between method tabs
- Check rankings and values
- Review statistics
- Examine visualizations

#### Step 7: Export
1. Click **"Export Results"**
2. Choose save location
3. Excel file contains all results

---

## 8. Methods Explained

### 1. Principal Component Analysis (PCA)

**Description:**
- Statistical method based on variance
- Reduces dimensionality
- Retains maximum information

**When to use:**
- Many correlated indicators
- Want objective weights
- Need dimension reduction

**Advantages:**
- Purely statistical
- Well-established method
- Handles correlation

**Limitations:**
- Assumes linear relationships
- May be hard to interpret
- Sensitive to outliers

**Weights based on:**
- Explained variance
- Factor loadings
- Varimax rotation

---

### 2. Shannon's Entropy

**Description:**
- Information theory approach
- Measures discriminatory power
- Higher entropy = less information

**When to use:**
- Want data-driven weights
- Value diversity of indicators
- Need objective approach

**Advantages:**
- Pure data-driven
- Simple to understand
- No assumptions needed

**Limitations:**
- Ignores correlations
- May give unexpected weights
- Sensitive to scale

**Weights based on:**
- Information content
- Degree of variation
- Discriminatory power

---

### 3. Benefit of the Doubt (BoD)

**Description:**
- DEA-based method
- Optimizes weights for each unit
- Maximizes performance

**When to use:**
- Allow flexible weights
- Want unit-specific weights
- Need maximum score

**Advantages:**
- Unit-specific weights
- No imposed structure
- Maximizes fairness

**Limitations:**
- Different weights per unit
- Can give unrealistic weights
- Computationally intensive

**Weights based on:**
- Linear programming
- Optimization
- Expert bounds (optional)

---

### 4. Equal Weights

**Description:**
- Simple arithmetic mean
- All indicators equally important
- Baseline method

**When to use:**
- No prior knowledge
- Want simplicity
- Baseline for comparison

**Advantages:**
- Simple and transparent
- Easy to understand
- No assumptions

**Limitations:**
- Ignores importance differences
- Ignores correlations
- May be too simple

**Weights:**
- All equal (1/n)

---

### 5. Geometric Mean

**Description:**
- Multiplicative aggregation
- Less compensatory
- Considers relative changes

**When to use:**
- Essential indicators
- Low values shouldn't be fully compensated
- Multiplicative relationships

**Advantages:**
- Less compensatory
- Suitable for percentages
- Handles zero better

**Limitations:**
- Requires positive values
- More complex interpretation
- Sensitive to low values

**Aggregation:**
- Product of indicators
- Weighted by importance

---

### 6. Harmonic Mean

**Description:**
- Least compensatory
- Emphasizes low values
- Used for rates/ratios

**When to use:**
- Critical indicators
- Poor performance unacceptable
- Want to penalize weakness

**Advantages:**
- Penalizes low values
- Suitable for rates
- Strong message

**Limitations:**
- Cannot handle zeros
- Very strict
- May be too harsh

**Aggregation:**
- Reciprocal of mean of reciprocals

---

### 7. Factor Analysis

**Description:**
- Assumes latent factors
- Similar to PCA
- Different assumptions

**When to use:**
- Believe in underlying factors
- Alternative to PCA
- Want latent structure

**Advantages:**
- Models latent structure
- Well-established
- Interpretable factors

**Limitations:**
- Assumptions about structure
- Computational complexity
- May not converge

**Weights based on:**
- Factor loadings
- Explained variance
- Rotation

---

### 8. Correlation-based Weighting

**Description:**
- Weights based on correlation
- Uses reference indicator
- Simple approach

**When to use:**
- Have reference indicator
- Want simple method
- Need interpretability

**Advantages:**
- Simple and intuitive
- Easy to explain
- Fast calculation

**Limitations:**
- Needs reference
- Ignores other relationships
- May be too simple

**Weights based on:**
- Correlation with reference
- Can use indicator or average

---

### 9. Minimal Uncertainty

**Description:**
- Combines multiple methods
- Minimizes ranking differences
- Consensus approach

**When to use:**
- After other methods
- Want robust ranking
- Need consensus

**Advantages:**
- Robust to method choice
- Combines information
- Stable rankings

**Limitations:**
- Requires other methods first
- Complex interpretation
- May mask differences

**Weights based on:**
- Optimization
- Ranking stability
- Multiple methods

---

## 9. Interpreting Results

### Understanding Output

Each method tab shows:

**1. Results Table**
- **Rank:** Position in ranking (1 = best)
- **CI:** Composite indicator value
- **Weights:** Indicator weights used

**2. Statistics**
- **Min:** Lowest CI value
- **Max:** Highest CI value
- **Mean:** Average CI value
- **Std Dev:** Standard deviation

**3. Visualizations**
- **Bar Chart:** Top 10 units
- **Histogram:** Distribution of CI values

### Comparing Methods

**High correlation (>0.9):**
- Methods agree strongly
- Results are robust
- Confident in rankings

**Medium correlation (0.7-0.9):**
- Some agreement
- Check for outliers
- Consider robustness

**Low correlation (<0.7):**
- Methods disagree
- Investigate differences
- May need data review

### Robustness Analysis

Check:
1. **Rank correlation:** Do methods agree on rankings?
2. **Top performers:** Are top units consistent?
3. **Weight stability:** Are weights reasonable?
4. **Sensitivity:** How much do results change?

---

## 10. Advanced Features

### Expert Opinion in BoD

Set weight bounds:
1. Expand "Setup BoD: Expert Opinion"
2. Enter min/max for each indicator
3. Values between 0 and 1
4. Sum of weights still = 1

Example:
- Indicator 1: Min = 0.2, Max = 0.5
- Indicator 2: Min = 0.1, Max = 0.4
- Indicator 3: Min = 0.2, Max = 0.6

### Programmatic Use

Use the package in your own scripts:

```python
from indicator import PCA_Calculation
import pandas as pd

# Your code here
data = pd.read_excel("data.xlsx")
model = PCA_Calculation(data)
results = model.run()
```

See `examples/example_usage.py` for more details.

---

## 11. Troubleshooting

### Common Issues

**"Module not found" error:**
```bash
pip install --upgrade -r requirements.txt
```

**"Python not found":**
- Reinstall Python
- Check "Add to PATH" option

**GUI doesn't open:**
```bash
pip install --upgrade customtkinter
```

**Calculation fails:**
- Check for missing data
- Ensure all indicators are numeric
- Reduce number of indicators
- Try different method

**Excel export fails:**
- Check file isn't already open
- Ensure write permissions
- Try different location

---

## 12. FAQ

**Q: How many indicators should I use?**
A: 3-10 is recommended. More than 15 may cause issues.

**Q: What if methods give different results?**
A: This is normal. Use correlation analysis and choose based on your objectives.

**Q: Can I use negative values?**
A: Yes, but normalize first. Geometric/Harmonic means need positive values.

**Q: How do I choose the best method?**
A: Depends on your objectives. Start with PCA and Entropy, then compare.

**Q: What normalization is used?**
A: Min-Max normalization. Direction determined by control variable correlation.

**Q: Can I change the color theme?**
A: Yes! The GUI adapts to your system (Light/Dark mode).

**Q: Is this suitable for academic research?**
A: Yes! Based on OECD guidelines and peer-reviewed literature.

**Q: How do I cite this tool?**
A: See README.md for citation information.

**Q: Can I use this for commercial purposes?**
A: Yes! MIT License allows commercial use.

**Q: Where can I get help?**
A: Email merwanroudane920@gmail.com or open GitHub issue.

---

## Appendices

### A. Mathematical Formulas

**Min-Max Normalization:**
```
Min-oriented: x_norm = (x - x_min) / (x_max - x_min)
Max-oriented: x_norm = (x_max - x) / (x_max - x_min)
```

**Weighted Arithmetic Mean:**
```
CI = Σ(w_i * x_i) / Σ(w_i)
```

**Geometric Mean:**
```
CI = (Π x_i^w_i)^(1/Σw_i)
```

**Harmonic Mean:**
```
CI = Σ(w_i) / Σ(w_i/x_i)
```

### B. References

1. OECD (2008). Handbook on Constructing Composite Indicators.
2. Nardo et al. (2005). Handbook on Constructing Composite Indicators.
3. Cherchye et al. (2007). Benefit of the Doubt Composite Indicators.

### C. Glossary

- **CI:** Composite Indicator
- **DMU:** Decision Making Unit
- **DEA:** Data Envelopment Analysis
- **PCA:** Principal Component Analysis
- **BoD:** Benefit of the Doubt

---

**For additional support:**
📧 merwanroudane920@gmail.com
🐙 https://github.com/merwanroudane/indic

---

*Manual Version 1.0.0*
*Last Updated: November 2024*
*© 2024 Dr. Merwan Roudane*
