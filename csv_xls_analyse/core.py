import io
import os
import zipfile
from pathlib import Path
from typing import Iterable, List

import pandas as pd


CSV_PARAMS = {
    'encoding': 'ISO-8859-1',
    'sep': ';',
    'quotechar': '"',
}


def _read_csv(path: str) -> pd.DataFrame:
    """Read a CSV file with default parameters."""
    df = pd.read_csv(path, **CSV_PARAMS)
    for col in df.select_dtypes(include='object').columns:
        if df[col].str.contains(',', na=False).any():
            df[col] = pd.to_numeric(df[col].str.replace(',', '.'), errors='ignore')
    return df


def _read_from_zip(path: str) -> List[pd.DataFrame]:
    """Extract CSV files from ZIP and return list of DataFrames."""
    frames = []
    with zipfile.ZipFile(path) as zf:
        for name in zf.namelist():
            if name.lower().endswith('.csv'):
                with zf.open(name) as f:
                    data = io.TextIOWrapper(f, encoding=CSV_PARAMS['encoding'])
                    df = pd.read_csv(data, sep=CSV_PARAMS['sep'], quotechar=CSV_PARAMS['quotechar'])
                    frames.append(df)
    return frames


def merge_csv_files(paths: Iterable[str]) -> pd.DataFrame:
    """Merge multiple CSV or ZIP files vertically into a single DataFrame."""
    frames = []
    for path in paths:
        p = Path(path)
        if p.suffix.lower() == '.csv':
            frames.append(_read_csv(str(p)))
        elif p.suffix.lower() == '.zip':
            frames.extend(_read_from_zip(str(p)))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def create_export_excel(df: pd.DataFrame, output) -> None:
    """Create the simple export workbook.

    OUTPUT can be a filepath or a file-like object.
    """
    with pd.ExcelWriter(output) as writer:
        df.to_excel(writer, sheet_name='Export', index=False)


def analyse_consumption(folder: str, output: str) -> None:
    """Generate the \"Moyenne conso DATA\" sheet from CSV files in folder."""
    csv_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith('.csv')]
    df = merge_csv_files(csv_files)
    if df.empty:
        raise ValueError('No CSV files found')

    df = df[df['Nom de la sous-rubrique'].str.startswith('Echanges')]

    df['Mois'] = pd.to_datetime(df['Période de la facture'], dayfirst=True).dt.strftime('%B-%y')
    volumes = df.groupby(['Numéro de l’utilisateur', 'Mois'])['Volume'].sum().unstack(fill_value=0)
    volumes = volumes[sorted(volumes.columns, key=lambda x: pd.to_datetime(x, format='%B-%y'), reverse=True)]

    result = volumes.copy()
    result['Total (Go)'] = volumes.sum(axis=1).div(1024).round(2)
    last4 = volumes.iloc[:, :4] if volumes.shape[1] >= 4 else volumes
    result['Moyenne (Go) 4 mois'] = last4.mean(axis=1).div(1024).round(2)
    result['Moyenne (Go) total'] = volumes.mean(axis=1).div(1024).round(2)
    result.reset_index(inplace=True)

    fixed_cols = ['Nom de la rubrique de niveau 1', 'Numéro de l’utilisateur',
                  'Nom de l’utilisateur', 'Prénom de l’utilisateur', 'Numéro de téléphone']
    fixed = df.drop_duplicates('Numéro de l’utilisateur')[fixed_cols]
    result = fixed.merge(result, on='Numéro de l’utilisateur', how='right')

    with pd.ExcelWriter(output, mode='w') as writer:
        result.to_excel(writer, sheet_name='Moyenne conso DATA', index=False)
