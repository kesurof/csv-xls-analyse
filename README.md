# CSV/XLS Analyse

This project provides tools to merge CSV files and analyse data consumption.

## Features

- Command line interface using **click**
- Streamlit application for uploading CSV/ZIP files and downloading Excel reports
- Functions to merge CSV files and generate Excel workbooks
- Generation of a sheet "Moyenne conso DATA" summarising monthly usage

## Installation

The project relies on `pandas` and `streamlit`. Install dependencies with:

```bash
pip install pandas streamlit openpyxl
```

## CLI usage

```
python -m csv_xls_analyse.cli merge file1.csv file2.zip -o output.xlsx
python -m csv_xls_analyse.cli moyenne-conso /path/to/folder -o Analyse.xlsx
```

## Streamlit app

Launch the app with:

```bash
streamlit run csv_xls_analyse/streamlit_app.py
```

The interface allows uploading multiple CSV or ZIP files, merging them and downloading the Excel result.
