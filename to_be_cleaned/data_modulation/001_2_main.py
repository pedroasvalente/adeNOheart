import pandas as pd
import numpy as np
import os
from BaselineRemoval import BaselineRemoval

# ---------------------------
# CONFIGURAÇÕES
# ---------------------------
INPUT_FILE = "001_1_all_excel.xlsx"
OUTPUT_FILE = "002_preprocessed_spectra.xlsx"

# ---------------------------
# FUNÇÕES
# ---------------------------

def load_data(file_path):
    """Carrega o Excel e renomeia a coluna NAM para sample_code."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Ficheiro não encontrado: {file_path}. Verifica o caminho ou move o ficheiro para o diretório atual.")
    df = pd.read_excel(file_path)
    if 'NAM' in df.columns:
        df.rename(columns={'NAM': 'sample_code'}, inplace=True)
    return df


def average_spectra(df):
    """Agrupa por sample_code e calcula a média das colunas espectrais."""
    # Colunas numéricas que representam espectros
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Remove path_length das colunas espectrais
    spectral_cols = [c for c in numeric_cols if c != 'path_length']
    # Agrupa e calcula média
    averaged = df.groupby('sample_code')[spectral_cols].mean().reset_index()
    return averaged, spectral_cols


def baseline_correction(spectrum):
    return BaselineRemoval(spectrum).ModPoly(4)


def euclidean_normalization(spectrum):
    norm = np.linalg.norm(spectrum)
    return spectrum / norm if norm != 0 else spectrum


def preprocess_spectra(df, spectral_cols):
    """Aplica correção de baseline e normalização a cada espectro."""
    df[spectral_cols] = df[spectral_cols].apply(
        lambda row: euclidean_normalization(baseline_correction(row.values)),
        axis=1,
        result_type='expand'
    )
    return df


def export_to_excel(df, output_file, sheet_name='Spectra'):
    """Exporta DataFrame para um ficheiro Excel."""
    df.to_excel(output_file, sheet_name=sheet_name, index=False)


def main():
    df = load_data(INPUT_FILE)
    df_avg, spectral_cols = average_spectra(df)
    df_pre = preprocess_spectra(df_avg, spectral_cols)
    export_to_excel(df_pre, OUTPUT_FILE)
    print(f"Preprocessed spectra saved to {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
