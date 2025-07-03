import pandas as pd

class BaseProcessador:
    def __init__(self):
        self._dados_processados: pd.DataFrame | None = None

    def get_dataframe(self) -> pd.DataFrame:
        if self._dados_processados is None:
            raise ValueError("Nenhum DataFrame processado disponível.")
        return self._dados_processados

    def exportar_para_excel(self, output_file: str, sheet_name: str = 'Main'):
        if self._dados_processados is None:
            raise ValueError("Nenhum dado processado. Corre primeiro o processamento.")
        self._dados_processados["DAY"] = self._dados_processados["DAY"].astype(str)
        self._dados_processados["TIME"] = self._dados_processados["TIME"].astype(str)
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            self._dados_processados.to_excel(writer, sheet_name=sheet_name, index=False)
        print(f"\u2705 Dados exportados para '{output_file}' com sucesso.")