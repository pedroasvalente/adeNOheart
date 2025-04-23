import pandas as pd
import numpy as np
from BaselineRemoval import BaselineRemoval
import re

from data_transformation import save_dataframe_to_csv

# Load Data
file_path = "001_1_all_excel.xlsx"
df = pd.read_excel(file_path)

def code_modulation(df):
    def extract_code(expression):
        match = re.search(r"^[^_]+_[^_]+_([^ -]+)", expression)
        return match.group(1) if match else None

    df["Extracted_Code"] = df["NAM"].apply(extract_code)
    df = df.drop(columns=["NAM"])
    df = df[["Extracted_Code"] + [col for col in df.columns if col != "Extracted_Code"]]
    return df

df = code_modulation(df)

def average_spectra(df):
    spectra_columns = df.columns[2:-2]  # assumes metadata in col 0-1 and last 2 cols
    averaged_df = df.groupby("Extracted_Code")[spectra_columns].mean().reset_index()
    return averaged_df, spectra_columns

df, spectra_columns = average_spectra(df)


def baseline_correction(spectrum):
    baseObj = BaselineRemoval(spectrum)
    return baseObj.ModPoly(4)

def euclidean_normalization(spectrum):
    norm = np.linalg.norm(spectrum)
    return spectrum / norm if norm != 0 else spectrum

def preprocess_spectrum(spectrum):
    spectrum = baseline_correction(spectrum)
    spectrum = euclidean_normalization(spectrum)
    return spectrum


df[spectra_columns] = df[spectra_columns].apply(
    lambda row: preprocess_spectrum(row.values),
    axis=1,
    result_type='expand'
)