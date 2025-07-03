import numpy as np
from base_processor import BaseProcessador
import pandas as pd
from BaselineRemoval import BaselineRemoval

class ModuladorEspectros(BaseProcessador):
    def __init__(self, df: pd.DataFrame):
        super().__init__()
        self._dados_processados = df.copy()
        self.meta_cols = ['NAM', 'DAY', 'TIME', 'path_length']
        self.spectral_cols = [
            col for col in df.columns
            if col not in self.meta_cols and df[col].dtype in [float, int]
        ]

    def aplicar_correcao_baseline(self):
        def corrigir(spectrum):
            return BaselineRemoval(spectrum).ModPoly(4)

        self._dados_processados[self.spectral_cols] = self._dados_processados[self.spectral_cols].apply(
            lambda row: corrigir(row.values), axis=1, result_type='expand'
        )

    def normalizar_euclidiano(self):
        def normalizar(spectrum):
            norm = np.linalg.norm(spectrum)
            return spectrum / norm if norm != 0 else spectrum

        self._dados_processados[self.spectral_cols] = self._dados_processados[self.spectral_cols].apply(
            lambda row: normalizar(row.values), axis=1, result_type='expand'
        )

    def agrupar_por_media(self):
        agrupado = self._dados_processados.groupby('NAM')[self.spectral_cols].mean().reset_index()
        meta = self._dados_processados.groupby('NAM')[['DAY', 'TIME', 'path_length']].first().reset_index()
        self._dados_processados = pd.merge(meta, agrupado, on='NAM')
