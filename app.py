import locale
import re
import zipfile
from io import BytesIO
from typing import List

import pandas as pd
import streamlit as st


def parse_volume(value: str) -> int:
    """Return the value in bytes from a string like '8 Go 206 Mo 633 Ko'."""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return 0
    text = str(value).replace(",", ".")
    go = mo = ko = 0.0
    m = re.search(r"([\d\.]+)\s*Go", text, re.IGNORECASE)
    if m:
        go = float(m.group(1))
    m = re.search(r"([\d\.]+)\s*Mo", text, re.IGNORECASE)
    if m:
        mo = float(m.group(1))
    m = re.search(r"([\d\.]+)\s*Ko", text, re.IGNORECASE)
    if m:
        ko = float(m.group(1))
    if go == mo == ko == 0:
        return 0
    return int(go * 1024 ** 3 + mo * 1024 ** 2 + ko * 1024)


def format_volume(value: int) -> str:
    """Format bytes to 'X Go Y Mo Z Ko'."""
    if value is None:
        return "0 Go 0 Mo 0 Ko"
    remain = int(value)
    go = remain // 1024 ** 3
    remain %= 1024 ** 3
    mo = remain // 1024 ** 2
    remain %= 1024 ** 2
    ko = remain // 1024
    return f"{go} Go {mo} Mo {ko} Ko"


def compute_moyenne_conso(df: pd.DataFrame) -> pd.DataFrame:
    """Generate the 'Moyenne conso DATA' sheet from merged data."""
    required_cols = [
        "Nom de la sous-rubrique",
        "Période de la facture",
        "Quantité ou volume",
        "Nom de la rubrique de niveau 1",
        "Numéro de l’utilisateur",
        "Nom de l’utilisateur",
        "Prénom de l’utilisateur",
        "Numéro de téléphone",
    ]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        return pd.DataFrame()

    mask = df["Nom de la sous-rubrique"].astype(str).str.startswith("Echanges", na=False)
    df = df.loc[mask].copy()
    if df.empty:
        return pd.DataFrame()

    df["date"] = pd.to_datetime(df["Période de la facture"], dayfirst=True, errors="coerce")
    df.dropna(subset=["date"], inplace=True)
    if df.empty:
        return pd.DataFrame()

    df["month"] = df["date"].dt.to_period("M")
    df["bytes"] = df["Quantité ou volume"].apply(parse_volume)

    id_cols = [
        "Nom de la rubrique de niveau 1",
        "Numéro de l’utilisateur",
        "Nom de l’utilisateur",
        "Prénom de l’utilisateur",
        "Numéro de téléphone",
    ]

    grouped = df.groupby(id_cols + ["month"])["bytes"].sum().reset_index()
    pivot = grouped.pivot(index=id_cols, columns="month", values="bytes").fillna(0)

    sorted_months = sorted(pivot.columns, reverse=True)
    total_bytes = pivot[sorted_months].sum(axis=1)
    n_months = len(sorted_months) if sorted_months else 1
    recent_months = sorted_months[:4]

    pivot["Total (Go)"] = (total_bytes / 1024 ** 3).round(2)
    pivot["Moyenne (Go) 4 mois"] = (
        pivot[recent_months].sum(axis=1) / (len(recent_months) * 1024 ** 3)
    ).round(2)
    pivot["Moyenne (Go) total"] = (total_bytes / (n_months * 1024 ** 3)).round(2)

    try:
        locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8")
    except locale.Error:
        pass

    month_map = {m: m.to_timestamp().strftime("%B-%y") for m in sorted_months}
    month_cols = [month_map[m] for m in sorted_months]
    pivot.rename(columns=month_map, inplace=True)
    for col in month_cols:
        pivot[col] = pivot[col].apply(lambda x: format_volume(int(x)))

    pivot.reset_index(inplace=True)

    column_order = id_cols + ["Total (Go)", "Moyenne (Go) 4 mois", "Moyenne (Go) total"] + month_cols
    pivot = pivot[column_order]
    return pivot


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
            for up_file in uploaded_files:
                filename = up_file.name
                if filename.lower().endswith(".csv"):
                    df = read_csv_file(up_file)
                    all_dfs.append(df)
                elif filename.lower().endswith(".zip"):
                    with zipfile.ZipFile(up_file) as zf:
                        dfs = extract_csv_from_zip(zf)
                        all_dfs.extend(dfs)
            if not all_dfs:
                st.error("Aucun fichier CSV n'a été trouvé.")
                return

            merged = pd.concat(all_dfs, ignore_index=True)
            moyenne_df = compute_moyenne_conso(merged)

            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                merged.to_excel(writer, sheet_name="Fusion", index=False)
                if not moyenne_df.empty:
                    moyenne_df.to_excel(
                        writer, sheet_name="Moyenne conso DATA", index=False
                    )
            buffer.seek(0)
            st.download_button(
                "Télécharger le fichier Excel",
                data=buffer,
                file_name="resultat.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )


if __name__ == "__main__":
    main()
