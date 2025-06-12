import zipfile
from io import BytesIO
from typing import List

import pandas as pd
import streamlit as st


def read_csv_file(file_data) -> pd.DataFrame:
    """Read a CSV file with predefined parameters."""
    df = pd.read_csv(
        file_data,
        encoding="ISO-8859-1",
        sep=";",
        quotechar='"',
    )
    # Convert columns with comma as decimal separator to float
    for col in df.select_dtypes(include="object").columns:
        if df[col].str.contains(",").any():
            df[col] = df[col].str.replace(" ", "")
            df[col] = df[col].str.replace(",", ".")
            try:
                df[col] = pd.to_numeric(df[col])
            except (ValueError, TypeError):
                pass
    return df


def extract_csv_from_zip(zf: zipfile.ZipFile) -> List[pd.DataFrame]:
    """Extract all CSV files from a ZipFile and return list of DataFrames."""
    dataframes = []
    for name in zf.namelist():
        if name.lower().endswith(".csv"):
            with zf.open(name) as f:
                df = read_csv_file(f)
                dataframes.append(df)
    return dataframes


def main():
    st.title("CSV/XLS Analyse")
    uploaded_files = st.file_uploader(
        "Importez des fichiers CSV ou ZIP", type=["csv", "zip"], accept_multiple_files=True
    )

    if uploaded_files:
        if st.button("Lancer la conversion"):
            all_dfs = []
            file_sheets = {}
            for up_file in uploaded_files:
                filename = up_file.name
                if filename.lower().endswith(".csv"):
                    df = read_csv_file(up_file)
                    file_sheets[filename] = df
                    all_dfs.append(df)
                elif filename.lower().endswith(".zip"):
                    with zipfile.ZipFile(up_file) as zf:
                        dfs = extract_csv_from_zip(zf)
                        for i, df in enumerate(dfs, 1):
                            sheet_name = f"{filename}_file{i}"
                            file_sheets[sheet_name] = df
                            all_dfs.append(df)
            if not all_dfs:
                st.error("Aucun fichier CSV n'a été trouvé.")
                return

            merged = pd.concat(all_dfs, ignore_index=True)
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                merged.to_excel(writer, sheet_name="Fusion", index=False)
                for sheet, df in file_sheets.items():
                    df.to_excel(writer, sheet_name=sheet[:31], index=False)
            buffer.seek(0)
            st.download_button(
                "Télécharger le fichier Excel",
                data=buffer,
                file_name="resultat.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


if __name__ == "__main__":
    main()
