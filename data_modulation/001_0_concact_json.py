import os
import json
import pandas as pd
import numpy as np
import re

# ---------------------------
# CONFIGURAÇÕES
# ---------------------------
folder_path = '../raw'  # pasta onde estão os JSONs
output_file = '001_1_all_excel.xlsx'  # ficheiro final Excel

# ---------------------------
# VARIÁVEIS INICIAIS
# ---------------------------
rows = []
wavelengths = []

# ---------------------------
# LEITURA DOS JSONs
# ---------------------------
for file_name in os.listdir(folder_path):
    if file_name.endswith('.json'):
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'r') as file:
            data = json.load(file)

        sample_origin_params = data.get("Sample Origin Parameters", {})
        ab_data = data.get("AB Data", [])
        data_status_params = data.get("Data Status Parameters", {})

        # Calcula os wavenumbers (só uma vez)
        if not wavelengths:
            fxv = data_status_params.get("FXV")
            lxv = data_status_params.get("LXV")
            npt = data_status_params.get("NPT")

            wavelengths = [
                fxv - ((i * (fxv - lxv)) / (npt - 1))
                for i in range(npt)
            ]

        row = [sample_origin_params.get("NAM"), sample_origin_params.get("INS")] + ab_data
        rows.append(row)

# ---------------------------
# CRIAÇÃO DO DATAFRAME
# ---------------------------
df = pd.DataFrame(rows)
df.columns = ["NAM", "INS"] + wavelengths

# Extrai o path length da coluna INS
df['raw_extracted'] = df['INS'].str.extract(r'path length:\s*([\d,\.]+)', expand=False)
df['path_length'] = df['raw_extracted'].str.replace(',', '.').astype(float)
df.drop(columns=['raw_extracted', 'INS'], inplace=True)
path_length_series = df.pop('path_length')
df.insert(1, 'path_length', path_length_series)

# ---------------------------
# EXTRAI sample_type do NAM
# ---------------------------
nam_pattern = r'^(?P<date>\d{8})_+(?P<sample_type>[^_]+)_'
extracted = df['NAM'].str.extract(nam_pattern)
sample_type_series = extracted['sample_type']

# ---------------------------
# SEPARA REGISTOS INVÁLIDOS
# ---------------------------
mask_invalid = sample_type_series.isna()
mask_tm = sample_type_series.notna() & (sample_type_series.str.upper() == 'TM')
mask_to_check = mask_invalid | mask_tm

to_check = df[mask_to_check].copy()
df_valid = df[~mask_to_check].copy()

# ---------------------------
# EXPORTAÇÃO PARA EXCEL
# ---------------------------
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    df_valid.to_excel(writer, sheet_name='Main', index=False)
    to_check.to_excel(writer, sheet_name='to_check', index=False)

print(f"Data exported to {output_file} with sheets 'Main' and 'to_check'.")