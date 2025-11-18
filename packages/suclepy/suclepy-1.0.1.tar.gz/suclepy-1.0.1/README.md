# 🧹 SUCLEPY — Smart Universal Cleaner Library for Python
![SUCLEPY Library](assets/library_image.png)
![Python](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.1-green?style=for-the-badge)
![License](https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge)

---

## ✨ Overview

**SUCLEPY v1.0.1** is a **Smart Universal Cleaner Library for Python** designed to make data cleaning **automatic, fast, and reliable**.  
It handles missing values, duplicates, invalid emails, date formatting, string normalization, and generates **detailed cleaning reports**.  
Perfect for **data scientists, analysts, and developers** working with messy datasets.

Compatible with **Python 3.11+**.

---

## 🗂 Version History


### v1.0.1
- String columns missing values filled with `"abcd"`  
- Dates automatically formatted to `DD-MM-YYYY`  
- Missing or invalid dates filled with `"00-00-0000"`  
- Emails missing entirely filled with `"abc@gmail.com"`  
- Emails with missing domain automatically corrected  
- Minor improvements to cleaning report generation and performance

### v1.0.0
- Automatic Cleaning: Dataset cleaned intelligently using default strategies
- Duplicate Removal: Repeated rows removed to avoid redundancy
- Missing Value Handling: Numeric missing values handled via mean/median; categorical via mode; rows can be dropped
- Email Validation: Detects invalid email addresses
- Date Parsing: Converts various date formats to standardized format
- Text Normalization: Capitalizes and strips unnecessary spaces
- CSV Export: Saves cleaned data easily
- Cleaning Report: Generates a clear and printable cleaning report
---

## ⚙️ Installation

```bash
pip install suclepy
```

---

## 🧩 Library Structure

SUCLEPY ke modules aur folder structure:

```text
suclepy/
├── __init__.py
├── core/
│   ├── __init__.py
│   ├── cleaner.py
│   ├── analyzer.py
│   ├── role_infer.py
│   ├── validator.py
│   └── reporter.py
└── utils.py

```


---

## 🧑‍💻 Usage Example

```python
import pandas as pd
import suclepy as sp

# Create a sample dataset with 10 rows
df = pd.DataFrame({
    "Name": ["Subodh", None, "", "Amit", "Riya", None, "Riya", "Mohan", "", "Geeta"],
    "Age": [21, None, 22, 25, 20, 23, 20, None, 24, 22],
    "Join_Date": [
        "2024/05/10", None, "12-05-2024", "2024-05-11", "May 12, 2024",
        "13/05/2024", "", "2024-05-14", None, "2024/05/15"
    ],
    "Email": [
        "subodh@", None, "amit@example.com", "amit@", "", "riya@gmail.com",
        None, "mohan@", "geeta@example.com", ""
    ],
    "City": [None, "Jaipur", "", "Delhi", None, "Mumbai", "Delhi", "", "Jaipur", "Pune"]
})

# Clean the dataset
report = sp.auto_clean(df)

# Print summary and cleaned data
print("=== Cleaning Summary ===")
print(report.summary())

print("\n=== Cleaned Data ===")
print(report.head(10))  # Show all 10 rows

# Save cleaned data to CSV
report.to_csv("cleaned_dataset.csv")


```

### 
```text
=== Cleaning Summary ===
SUCLEPY CLEANING REPORT
------------------------------
Total Rows (before): 10
Rows After Cleaning: 10
Duplicates Removed: 0
Missing Values Filled: 10
Invalid Emails Fixed: 7
Missing Strings Filled: 5
Dates Standardized: 7
Default Date Used: 3
Status: SUCCESS ✅

=== Cleaned Data ===
     Name   Age   Join_Date              Email    City
0  Subodh  21.0  05-10-2024   subodh@gmail.com    abcd
1    abcd  22.0  00-00-0000      abc@gmail.com  Jaipur
2    abcd  22.0  12-05-2024   amit@example.com    abcd
3    Amit  25.0  05-11-2024     amit@gmail.com   Delhi
4    Riya  20.0  12-05-2024      abc@gmail.com    abcd
5    abcd  23.0  13-05-2024     riya@gmail.com  Mumbai
6    Riya  20.0  00-00-0000      abc@gmail.com   Delhi
7   Mohan  22.0  14-05-2024    mohan@gmail.com    abcd
8    abcd  24.0  00-00-0000  geeta@example.com  Jaipur
9   Geeta  22.0  15-05-2024      abc@gmail.com    Pune

File saved as cleaned_dataset.csv

```

---

## 🔧 Configuration Options

```python
import suclepy as sp

sp.config({
    "fill_missing_strategy": "mean",     # Strategy for numeric missing values
    "fill_string": "abcd",               # Fill string missing values
    "fill_date": "00-00-0000",           # Fill invalid/missing dates
    "validate_email": True,              # Validate emails
    "auto_correct_email": True,          # Auto-fix incomplete emails
    "drop_duplicates": True,             # Remove duplicate rows
    "date_format": "DD-MM-YYYY"          # Standard date format
})
```

---

## 📝 Cleaning Rules / Behavior

- **String Columns**: missing (`None`, `NaN`, `""`) → `"abcd"`  
- **Dates**: any format → standardized to `DD-MM-YYYY`, missing → `"00-00-0000"`  
- **Emails**: missing → `"abc@gmail.com"`, incomplete domains auto-corrected  
- **Numeric Columns**: missing → `mean` or configured strategy  
- **Duplicates**: automatically removed  
- **Text Normalization**: capitalized and stripped extra spaces  


---

## ❓ FAQ / Notes

**Q1:** What happens if an email has no `@` or domain?  
**A:** Automatically corrected or filled with `"abc@gmail.com"`  

**Q2:** How are missing dates handled?  
**A:** Any invalid/missing date is replaced with `"00-00-0000"`  

**Q3:** Can I customize fill values?  
**A:** Yes, see **Configuration Options** above  

**Q4:** Compatible Python versions?  
**A:** Python 3.11+  

---

## 📚 Documentation & Resources

- **GitHub Repository:** [https://github.com/subodhkryadav/suclepy](https://github.com/subodhkryadav/suclepy)  
- **LinkedIn:** [Subodh Kumar Yadav](https://www.linkedin.com/in/subodh-kumar-yadav-522828293)  

---

## 📝 License

This project is licensed under the **MIT License**.
