from class_data_concat import ProcessadorDadosLab
from class_data_modulation import ModuladorEspectros

def main():
    # importante!!! é necessário colocar aqui o folderpath onde estão os ficheiros json retirados da máquina!
    folder_path = "to_be_cleaned/raw"

    # 1. Processamento inicial
    processador = ProcessadorDadosLab(folder_path=folder_path)
    linhas, _ = processador.carregar_dados_json()
    df_raw = processador.criar_dataframe(linhas)

    # 2. Modulação (aplica os passos desejados)
    modulador = ModuladorEspectros(df_raw)
    modulador.aplicar_correcao_baseline()
    modulador.normalizar_euclidiano()
    modulador.agrupar_por_media()

    # 3. Exportação para Excel
    modulador.exportar_para_excel("resultado_final.xlsx")

if __name__ == '__main__':
    main()