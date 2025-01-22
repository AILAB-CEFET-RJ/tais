# TAIS APP

Tool for analisys of AIS data

## Sumário

1. [Execução do Servidor Back-End](#execução-do-servidor-back-end)
   - [Para executar no ambiente de Desenvolvimento (DEV)](#para-executar-no-ambiente-de-desenvolvimento-dev)
   - [Alternativamente para rodar a aplicação sem o encapsulamento do Docker](#alternativamente-para-rodar-a-aplicação-sem-o-encapsulamento-do-docker)
2. [Instruções sobre a utilização da API](#instruções-sobre-a-utilização-da-api)
   - [Mapa de Calor (Heatmap) (GET)](#1-mapa-de-calor-heatmap--get-)
   - [Dados do Mapa de Calor (Heatmap) (GET)](#2-dados-do-mapa-de-calor-heatmap--get-)
   - [Filtragem por Intervalo de Tempo (GET)](#3-filtragem-por-intervalo-de-tempo--get-)
   - [Retorno de Embarcação por Identificador Único (GET)](#4-retorno-de-embarcação-por-identificador-único--get-)
3. [Formato de dados AIS utilizado no Tais](#formato-de-dados-ais-utilizado-no-tais)
   - [Organização das pastas](#organização-das-pastas)
   - [Processamento dos dados CSV](#processamento-dos-dados-csv)
      - [Campos do CSV](#campos-do-csv)
4. [Observações](#observações)

## Execução do Servidor Back-End

### Para executar no ambiente de Desenvolvimento (DEV)

1. Execute o terminal
2. Execute o comando ```docker compose up -d --build``` para gerar a imagem da máquina e executar o container que irá rodar a API. Após a execução do comando, deverá aparecer em um Log gerado pelo Flask, a URL em que a aplicação está rodando. Ex: <http://localhost:5000>

### Alternativamente para rodar a aplicação sem o encapsulamento do Docker

1. Execute o terminal
2. Vá para o diretório com o comando ```cd api/app```
3. Crie e ative a venv ```python -m venv venv``` e em seguida ```venv\Scripts\activate```
4. Instale as dependências executando o comando ```pip install -r requirements.txt```
5. Execute o comando ```python app.py``` para rodar a aplicação flask diretamente
6. Após a execução do comando, deverá aparecer em um Log gerado pelo Flask, a URL em que a aplicação está rodando. Ex: <http://localhost:5000>

## Instruções sobre a utilização da API

### 1. Mapa de Calor (Heatmap) ( GET )

- **Rota**: /visualization

- **Exemplo**: <http://127.0.0.1:5000/visualization?vesselId=IHS-AIS-209016000&startTime=2024-08-29%2000:08:54&endTime=2024-08-29%2023:56:13>

- **Descrição**: Permite a visualização de um mapa de calor baseado nos dados AIS
disponíveis. Este mapa de calor pode ser utilizado para identificar áreas de alta ou
baixa densidade de tráfego marítimo. Pode-se especificar o vesselId da embarcação, o tempo de início e o tempo final para análise

### 2. Mapa de Calor (Heatmap) com bounding-box ( GET )

- **Rota**: /visualization

- **Exemplo**: <http://127.0.0.1:5000/visualization?vesselId=IHS-AIS-100001974&startTime=2024-08-29%2013:01:21&endTime=2024-08-29%2023:31:17&bbox=-23.116365,-43.304672,-22.816061,-42.867279>

- **Descrição**: Permite a visualização de um mapa de calor baseado nos dados AIS
disponíveis, tendo em consideração uma área delimitada por dois pares de coordenadas indicadas pelo usuário. Este mapa de calor pode ser utilizado para identificar áreas de alta ou baixa densidade de tráfego marítimo. Assim como no item anterior, pode-se especificar o vesselId da embarcação, o tempo de início e o tempo final para análise

### 3. Dados do Mapa de Calor (Heatmap) ( GET )

- **Rota**: /api/heatmap_csv

- **Exemplo**: <http://127.0.0.1:5000/api/heatmap_csv?vesselId=IHS-AIS-209016000&startTime=2024-08-29%2000:08:54&endTime=2024-08-29%2023:56:13>

- **Descrição**: Retorna os dados puros de um mapa de calor baseado nos dados AIS
disponíveis. Estes dados podem ser usados na construção de um mapa de calor ou simplesmente para análise direta. Pode-se especificar o vesselId da embarcação, o tempo de início e o tempo final para análise

### 4. Filtragem por Intervalo de Tempo ( GET )

- Baixe o arquivo ```historico_acompanhamentos_24horas.csv``` e coloque-o no mesmo diretório que o ```app.py```.

- Ao rodar a consulta, será gerado um arquivo ordenado chamado ```sorted_historico_acompanhamentos_24horas.csv```.

- **Rota**: <http://127.0.0.1:5000/vessel/timestamp/start/end>

- **Exemplo**: <http://127.0.0.1:5000/vessel/timestamp/2024-08-13%2000:00:00/2024-08-13%2000:10:00>

- **Descrição**: Filtra as observações de embarcações por um intervalo de tempo específico. Essa funcionalidade é útil para análises temporais. No exemplo, as observações entre meia-noite e 00:10 do dia 13 de agosto de 2024 são filtradas.

### 5. Retorno de Embarcação por Identificador Único ( GET )

- Para fazer essa consulta, também é necessário baixar o arquivo ```historico_acompanhamentos_24horas.csv``` e colocá-lo no mesmo diretório que o ```app.py```. Se isso não foi feito anteriormente, é necessário realizá-lo agora.

- **Rota**: <http://127.0.0.1:5000/vessel/vessel_id>

- **Exemplo**: <http://127.0.0.1:5000/vessel/IHS-AIS-205188000>

- **Descrição**: Esta funcionalidade permite retornar os dados de uma embarcação específica através de seu identificador único. É útil para acessar rapidamente as informações detalhadas de uma embarcação.

## Formato de dados AIS utilizado no Tais

A aplicação utiliza o formato JSON para representar as informações de rastreamento de embarcações em tempo real. Abaixo está a estrutura de dados AIS processada, que contém dados detalhados sobre a posição das embarcações, incluindo coordenadas geográficas, velocidade, rumo e outros parâmetros relevantes.

### Organização das pastas

1. ```img```: local onde são salvas as imagens geradas pela API

2. ```routes/```: Contém os arquivos responsáveis pelas rotas da aplicação Flask, divididas por responsabilidade:
    **home.py**: Rota inicial e informações gerais da API.
    **heatmap.py**: Rotas relacionadas aos mapas de calor.
    **vessel.py**: Rotas para consultas e filtragens de dados de embarcações.
    **visualization.py**: Rotas para visualização dos dados

3. ```services/```: Implementa a lógica da aplicação, separando as funcionalidades em serviços reutilizáveis:
    **heatmap_service.py**: Funções para cálculos de heatmaps.
    **vessel_service.py**: Manipulação de dados relacionados a embarcações.
    **file_service.py**: Normalização de timestamps e conversões de dados.

4. ```resources/```: Contém os arquivos de dados usados pela aplicação, como o CSV com as trajetórias.

### Processamento dos dados CSV

A aplicação utiliza o arquivo ```historico_acompanhamentos_24horas.csv```, que contém dados históricos de rastreamento. O CSV é lido e processado, permitindo a consulta de dados filtrados por timestamp ou ID da embarcação. Quando necessário, o arquivo é ordenado para garantir que os dados sejam manipulados de forma cronológica.

#### Campos do CSV

O arquivo ```historico_acompanhamentos_24horas.csv``` possui as seguintes colunas principais:

| **Coluna**   | **Descrição**                                  |
|--------------|------------------------------------------------|
| `vesselId`   | Identificador único da embarcação              |
| `long`       | Longitude da posição da embarcação             |
| `lat`        | Latitude da posição da embarcação              |
| `rumo`       | Rumo da embarcação em graus                    |
| `velocidade` | Velocidade da embarcação em nós                |
| `timestamp`  | Carimbo de data e hora do evento (em formato `YYYY-MM-DD HH:MM:SS`) |
| `origem`     | tecnologia ou sistema de monitoramento utilizado (ex: AIS)                     |
| `subOrigem`  |  Origem adicional ou especificação do tipo de monitoramento (ex: Satelital)      |

## Observações

- Os dados brutos utilizados pela API são gerados de arquivos CSV armazenados localmente. No repositorio encontram-se recortes de dados menores desses arquivos para facilitar o processamento.

- Certifique-se de que os arquivos necessários estejam no diretório correto antes de executar as funcionalidades da API.
