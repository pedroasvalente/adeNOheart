import os
import json
import pandas as pd
import re
from typing import List, Dict, Optional, Tuple
from base_processor import BaseProcessador

class ProcessadorDadosLab(BaseProcessador):
    def __init__(self, folder_path: str):
        super().__init__()
        self.folder_path = folder_path
        self._comprimentos_onda: List[float] = []

    def _calcular_comprimentos_onda(self, params_status: Dict) -> List[float]:
        fxv = params_status.get("FXV")
        lxv = params_status.get("LXV")
        npt = params_status.get("NPT")

        if fxv is not None and lxv is not None and npt:
            return [fxv - ((i * (fxv - lxv)) / (npt - 1)) for i in range(npt)]

        raise ValueError("Parâmetros FXV, LXV ou NPT ausentes ou inválidos no JSON.")

    def _limpar_nam(self, nam_raw: str) -> Optional[str]:
        if not isinstance(nam_raw, str):
            return None

        nam_limpo = nam_raw.split('-')[0].strip()

        if re.match(r'^\d{8}_', nam_limpo):
            partes = nam_limpo.split('_')
            if len(partes) >= 3:
                return '_'.join(partes[2:])

        return nam_limpo

    def carregar_dados_json(self) -> Tuple[List[List], List[float]]:
        linhas = []

        for nome_arquivo in os.listdir(self.folder_path):
            if nome_arquivo.lower().endswith('.json'):
                caminho_arquivo = os.path.join(self.folder_path, nome_arquivo)
                with open(caminho_arquivo, 'r') as f:
                    dados = json.load(f)

                origem_amostra = dados.get("Sample Origin Parameters", {})
                dados_ab = dados.get("AB Data", [])
                params_status = dados.get("Data Status Parameters", {})

                if not self._comprimentos_onda:
                    self._comprimentos_onda = self._calcular_comprimentos_onda(params_status)

                nam_raw = origem_amostra.get("NAM", "")
                nam_limpo = self._limpar_nam(nam_raw)
                if nam_limpo and 'TM' in nam_limpo.upper():
                    continue

                ins = origem_amostra.get("INS", "")
                data = params_status.get("DAT", "")
                hora = params_status.get("TIM", "")
                linha = [nam_limpo, data, hora, ins] + dados_ab
                linhas.append(linha)

        return linhas, self._comprimentos_onda

    def criar_dataframe(self, linhas: List[List]) -> pd.DataFrame:
        if not self._comprimentos_onda:
            raise ValueError("Comprimentos de onda não definidos.")

        df = pd.DataFrame(linhas)
        df.columns = ["NAM", "DAY", "TIME", "INS"] + [str(comp) for comp in self._comprimentos_onda]

        df['raw_extracted'] = df['INS'].str.extract(r'path length:\s*([\d\.,]+)', expand=False)
        df['path_length'] = pd.to_numeric(df['raw_extracted'].str.replace(',', '.'), errors='coerce')
        df.drop(columns=['raw_extracted', 'INS'], inplace=True)
        colunas_fixas = ['NAM', 'DAY', 'TIME', 'path_length']
        colunas_comprimentos = [col for col in df.columns if col not in colunas_fixas]
        df = df[colunas_fixas + colunas_comprimentos]

        self._dados_processados = df
        return df
