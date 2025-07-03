import os
import json
import pandas as pd
import re

# ---------------------------
# CONFIGURAÇÕES
# ---------------------------
FOLDER_PATH = '../raw'
OUTPUT_FILE = '001_1_all_excel.xlsx'

# ---------------------------
# FUNÇÕES
# ---------------------------

def get_wavenumbers(data_status_params):
    """Calcula wavenumbers a partir dos parâmetros do JSON."""
    fxv = data_status_params.get("FXV")
    lxv = data_status_params.get("LXV")
    npt = data_status_params.get("NPT")

    if fxv is not None and lxv is not None and npt:
        return [
            fxv - ((i * (fxv - lxv)) / (npt - 1))
            for i in range(npt)
        ]
    return []


def clean_nam(nam_raw):
    """Limpa o NAM inicial removendo sufixo após '-' e data prefixo se existir."""
    if not isinstance(nam_raw, str):
        return None

    # Remove tudo após o primeiro hífen
    nam_cleaned = nam_raw.split('-')[0].strip()

    # Se começa com data (8 dígitos + '_'), remove prefixo até 3º bloco
    if re.match(r'^\d{8}_', nam_cleaned):
        parts = nam_cleaned.split('_')
        if len(parts) >= 3:
            return '_'.join(parts[2:])
    # Caso contrário, mantém o NAM limpo (sem sufixo)
    return nam_cleaned


def load_json_data(folder_path):
    """Lê todos os JSONs da pasta, extrai NAM limpo, INS e AB Data."""
    rows = []
    wavelengths = []

    for file_name in os.listdir(folder_path):
        if file_name.lower().endswith('.json'):
            file_path = os.path.join(folder_path, file_name)
            with open(file_path, 'r') as f:
                data = json.load(f)

            sample_origin = data.get("Sample Origin Parameters", {})
            ab_data = data.get("AB Data", [])
            status_params = data.get("Data Status Parameters", {})

            # Calcula wavenumbers apenas na primeira iteração
            if not wavelengths:
                wavelengths = get_wavenumbers(status_params)

            # Extrai NAM limpo e descarta TMs
            nam_raw = sample_origin.get("NAM", "")
            nam_cleaned = clean_nam(nam_raw)
            # Descartar se contiver TM
            if nam_cleaned and 'TM' in nam_cleaned.upper():
                continue

            ins = sample_origin.get("INS", "")
            row = [nam_cleaned, ins] + ab_data
            rows.append(row)

    return rows, wavelengths


def build_dataframe(rows, wavelengths):
    """Cria DataFrame e extrai path_length."""
    df = pd.DataFrame(rows)
    df.columns = ["NAM", "INS"] + wavelengths

    # Extrai path length
    df['raw_extracted'] = df['INS'].str.extract(r'path length:\s*([\d\.,]+)', expand=False)
    df['path_length'] = df['raw_extracted'].str.replace(',', '.').astype(float)
    df.drop(columns=['raw_extracted', 'INS'], inplace=True)
    df.insert(1, 'path_length', df.pop('path_length'))

    return df


def export_to_excel(df, output_file):
    """Exporta o DataFrame para ficheiro Excel."""
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Main', index=False)
    print(f"Data exported to '{output_file}' on sheet 'Main'.")

# ---------------------------
# EXECUÇÃO PRINCIPAL
# ---------------------------

def main():
    rows, wavelengths = load_json_data(FOLDER_PATH)
    df = build_dataframe(rows, wavelengths)
    export_to_excel(df, OUTPUT_FILE)

if __name__ == '__main__':
    main()
