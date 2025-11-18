# 🚀 Quick Start Guide

**Composite Indicator Builder by Dr. Merwan Roudane**

---

## Installation (3 Steps)

### Step 1: Install Python
- Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
- Make sure to check "Add Python to PATH" during installation

### Step 2: Download the Package
```bash
git clone https://github.com/merwanroudane/indic.git
cd indic
```

### Step 3: Install
```bash
pip install -e .
```

---

## Launch Application

### Windows
Double-click `launch.bat` or run:
```cmd
indicator
```

### Mac/Linux
Run:
```bash
./launch.sh
```

Or:
```bash
indicator
```

---

## First Use (5 Minutes)

### 1. Prepare Your Data
Create an Excel file with:
- **Rows:** Your units (countries, companies, regions, etc.)
- **Columns:** Your indicators (numeric values)
- **Optional:** One column for labels/names

Example:
| Country | GDP | Education | Health | Innovation |
|---------|-----|-----------|--------|------------|
| USA     | 65  | 0.92      | 78.5   | 75         |
| Germany | 48  | 0.95      | 81.0   | 70         |

### 2. Load Your Data
- Click **"Load Excel File"**
- Select your file
- Preview appears automatically

### 3. Select Indicators
- Check boxes next to indicators you want to use
- Choose label column (optional)
- Choose control variable (optional)

### 4. Choose Methods
Select one or more:
- ☑ **PCA** - Principal Component Analysis
- ☑ **Entropy** - Shannon's Entropy
- ☑ **BoD** - Benefit of the Doubt
- ☐ Equal Weights
- ☐ Geometric Mean
- ☐ And more...

### 5. Calculate & Export
- Click **"Calculate Indicators"**
- View results in tabs
- Click **"Export Results"** to save as Excel

---

## Troubleshooting

### "Python not found"
- Reinstall Python
- Make sure "Add to PATH" is checked

### "Module not found"
```bash
pip install --upgrade -r requirements.txt
```

### "Import Error"
```bash
pip install --upgrade customtkinter
```

---

## Contact

**Dr. Merwan Roudane**
- Email: merwanroudane920@gmail.com
- GitHub: [merwanroudane/indic](https://github.com/merwanroudane/indic)

---

**Need help?** Open an issue on GitHub or send an email!
