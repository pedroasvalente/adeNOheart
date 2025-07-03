# adeNOheart


README - Processamento e Modulação de Dados FTIR

Visão Geral

Este projeto é uma pipeline modular para processamento de dados espectrais FTIR extraídos de ficheiros JSON. O fluxo principal consiste em:
	•	Carregar e organizar os dados brutos (JSON) numa estrutura tabular (DataFrame) organizada.
	•	Aplicar técnicas de modulação e pré-processamento espectral, como correção de baseline e normalização.
	•	Exportar os resultados para ficheiros Excel para análise e uso posterior.

⸻

Estrutura dos Ficheiros

1. base_processor.py

Classe base BaseProcessador que define funcionalidades comuns para os processadores de dados:
	•	Armazena o DataFrame processado internamente.
	•	Permite obter o DataFrame via método get_dataframe().
	•	Implementa método exportar_para_excel(output_file: str) para exportar o DataFrame para Excel.

Esta classe serve como base para as outras classes que implementam funcionalidades específicas.

⸻

2. class_data_concat.py

Classe ProcessadorDadosLab especializada em:
	•	Ler e interpretar ficheiros JSON da pasta de dados brutos.
	•	Extrair informações relevantes (e.g., NAM, DAY, TIME, espectros).
	•	Calcular os comprimentos de onda e organizar os dados num DataFrame bem estruturado.
	•	Herda da classe base para funcionalidades comuns.

Métodos principais:
	•	carregar_dados_json(): lê JSONs e extrai dados.
	•	criar_dataframe(linhas): cria o DataFrame organizado.
	•	Usa o método da base para exportar para Excel.

⸻

3. class_data_modulation.py

Classe ModuladorEspectros que recebe um DataFrame e aplica pré-processamentos espectrais:
	•	Correção de baseline usando a biblioteca BaselineRemoval.
	•	Normalização euclidiana dos espectros.
	•	Agrupamento por média dos espectros, mantendo metadados.
	•	Herdando da classe base para exportação e acesso ao DataFrame.

Permite modular o DataFrame sem alterar a estrutura das colunas.

⸻

4. main.py

Script principal que orquestra:
	•	Instancia o ProcessadorDadosLab para carregar e preparar os dados.
	•	Instancia o ModuladorEspectros para aplicar pré-processamentos.
	•	Exporta os dados organizados e modulados para ficheiros Excel distintos.

⸻

Como Usar
	1.	Definir o caminho da pasta com ficheiros JSON na variável folder_path no main.py.
	2.	Executar o main.py para processar os dados e gerar os ficheiros Excel.
	3.	Modificar o main.py para ajustar parâmetros, aplicar ou não a modulação espectral.

⸻

Dependências
	•	Python 3.8+
	•	pandas
	•	numpy
	•	BaselineRemoval
	•	openpyxl

Instalação via pip:

pip install pandas numpy BaselineRemoval openpyxl

Estrutura Esperada dos Dados
	•	Ficheiros JSON na pasta de input, com estrutura contendo:
	•	"Sample Origin Parameters" com NAM, INS e outros.
	•	"Data Status Parameters" com DAT, TIM, FXV, LXV, NPT, etc.
	•	"AB Data" com os espectros.
	•	O DataFrame resultante terá sempre colunas fixas:

 NAM | DAY | TIME | path_length | <comprimentos_onda...>
