import os
import json
import pandas as pd
from loguru import logger

# Configure loguru logging
logger.add("pipeline.log", format="{time} {level} {message}", level="INFO", rotation="10 MB", compression="zip")


def load_json_files_from_folder(folder_path):
    """
    Carrega todos os arquivos JSON de uma pasta e retorna uma lista de DataFrames normalizados.

    Args:
        folder_path (str): Caminho para a pasta contendo os arquivos JSON.

    Returns:
        list: Lista de DataFrames carregados e normalizados.
    """
    dataframes = []  # Lista para guardar os DataFrames

    logger.info(f"Iniciando o carregamento de arquivos JSON da pasta: {folder_path}")
    for filename in os.listdir(folder_path):
        if filename.endswith(".json"):
            file_path = os.path.join(folder_path, filename)

            try:
                with open(file_path, 'r') as file:
                    data = json.load(file)

                    # Normalizar o JSON para transformar em DataFrame
                    if isinstance(data, list):  # Caso seja uma lista de dicionários
                        df = pd.json_normalize(data)
                    elif isinstance(data, dict):  # Caso seja um único dicionário
                        df = pd.json_normalize([data])
                    else:
                        logger.warning(f"Formato não suportado no arquivo: {filename}")
                        continue

                    dataframes.append(df)
                    logger.info(f"Arquivo {filename} carregado com sucesso!")

            except (ValueError, TypeError, json.JSONDecodeError) as e:
                logger.error(f"Erro ao processar o arquivo {filename}: {e}")

    logger.info(f"Foram carregados {len(dataframes)} arquivos JSON com sucesso.")
    return dataframes


def concatenate_dataframes(dataframes):
    """
    Concatena uma lista de DataFrames em um único DataFrame.

    Args:
        dataframes (list): Lista de DataFrames.

    Returns:
        DataFrame: DataFrame único com todas as informações concatenadas.
    """
    if dataframes:  # Verificar se há DataFrames na lista
        logger.info("Iniciando a concatenação dos DataFrames.")
        concatenated_df = pd.concat(dataframes, ignore_index=True)
        logger.info(f"Concatenação finalizada. Total de registros no DataFrame: {len(concatenated_df)}")
        return concatenated_df
    else:
        logger.warning("Nenhum DataFrame foi carregado para concatenação.")
        return pd.DataFrame()  # Retorna um DataFrame vazio caso a lista esteja vazia


def clean_data(dataframe):
    """
    Aplica tratamento e limpeza nos dados, como remoção de valores nulos e renomeação de colunas.

    Args:
        dataframe (DataFrame): O DataFrame a ser tratado.

    Returns:
        DataFrame: O DataFrame processado.
    """
    logger.info("Iniciando a limpeza dos dados...")
    dataframe = dataframe.dropna()  # Remove linhas com valores nulos
    dataframe = dataframe.reset_index(drop=True)  # Reseta os índices
    logger.info(f"Número de registros após limpeza: {len(dataframe)}")
    return dataframe


def transform_data(dataframe):
    """
    Realiza transformações nos dados, como criação de novas colunas ou transformações baseadas em regras.

    Args:
        dataframe (DataFrame): O DataFrame a ser transformado.

    Returns:
        DataFrame: O DataFrame transformado.
    """
    logger.info("Iniciando as transformações nos dados...")

    # Exemplo: Adicionando uma coluna fictícia "processed" para marcar as linhas processadas
    dataframe["processed"] = True

    # (Adicione aqui as transformações específicas do seu contexto)

    logger.info("Transformações concluídas.")
    return dataframe


def save_dataframe_to_csv(dataframe, output_file):
    """
    Salva um DataFrame em um arquivo CSV.

    Args:
        dataframe (DataFrame): O DataFrame a ser salvo.
        output_file (str): Nome do arquivo de saída CSV.
    """
    try:
        dataframe.to_csv(output_file, index=False)
        logger.info(f"DataFrame salvo com sucesso no arquivo: {output_file}")
    except Exception as e:
        logger.error(f"Erro ao salvar o arquivo CSV: {e}")


def main():
    """
    Função principal do programa, responsável por organizar o fluxo de execução.
    """
    folder_path = "raw_data"  # Pasta onde estão os arquivos JSON
    output_file = "final_dataframe.csv"  # Nome do arquivo CSV de saída

    logger.info("Iniciando o pipeline de tratamento de dados.")

    # Etapa 1: Carregar os arquivos JSON e transformar em DataFrames
    dataframes = load_json_files_from_folder(folder_path)

    # Etapa 2: Concatenar todos os DataFrames
    final_df = concatenate_dataframes(dataframes)

    if not final_df.empty:  # Checar se o DataFrame final não está vazio
        # Etapa 3: Limpar os dados
        final_df = clean_data(final_df)

        # Etapa 4: Transformar os dados
        final_df = transform_data(final_df)

        # Etapa 5: Salvar o DataFrame no arquivo CSV
        save_dataframe_to_csv(final_df, output_file)
    else:
        logger.warning("Nenhum dado válido foi encontrado na pasta.")

    logger.info("Pipeline de tratamento finalizado.")


# Executar o programa
if __name__ == "__main__":
    main()
