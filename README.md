# TAIS APP

Tool for analisys of AIS data

## Sumário

1. [Execução do Servidor Back-End](#execução-do-servidor-back-end)
   - [Para executar no ambiente de Desenvolvimento (DEV)](#para-executar-no-ambiente-de-desenvolvimento-dev)
   - [Alternativamente para rodar a aplicação sem o encapsulamento do Docker](#alternativamente-para-rodar-a-aplicação-sem-o-encapsulamento-do-docker)
2. [Instruções sobre a utilização da API](#instruções-sobre-a-utilização-da-api)
   - [Visualização de Dados Processados (GET)](#1-visualização-de-dados-processados--get-)
   - [Mapa de Calor (Heatmap) (GET)](#2-mapa-de-calor-heatmap--get-)
   - [Filtragem por Intervalo de Tempo (GET)](#3-filtragem-por-intervalo-de-tempo--get-)
   - [Retorno de Embarcação por Identificador Único (GET)](#4-retorno-de-embarcação-por-identificador-único--get-)
3.[Formato de dados AIS utilizado no Tais](#formato-de-dados-ais-utilizado-no-tais)
   - [Organização das pastas](#organização-das-pastas)
   - [Processamento dos dados CSV](#processamento-dos-dados-csv)
      - [Campos do CSV](#campos-do-csv)
   -[Descrição dos campos JSON](#descrição-dos-campos-json)
4.[Observações](#observações)

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

### 1. Visualização de Dados Processados ( GET )

- **Rota**: /api/data

- **Descrição**: Esta funcionalidade permite o acesso a dados processados em formato
JSON. Os dados podem ser utilizados para análise, visualização ou integração com
outras aplicações.

### 2. Mapa de Calor (Heatmap) ( GET )

- **Rota**: /api/heatmap

- **Descrição**: Permite a visualização de um mapa de calor baseado nos dados AIS
disponíveis. Este mapa de calor pode ser utilizado para identificar áreas de alta ou
baixa densidade de tráfego marítimo.

### 3. Filtragem por Intervalo de Tempo ( GET )

- Baixe o arquivo ```historico_acompanhamentos_24horas.csv``` e coloque-o no mesmo diretório que o ```app.py```.

- Ao rodar a consulta, será gerado um arquivo ordenado chamado ```sorted_historico_acompanhamentos_24horas.csv```.

- **Rota**: <http://127.0.0.1:5000/timestamp/start/end>

- **Exemplo**: <http://127.0.0.1:5000/timestamp/2024-08-13%2000:00:00/2024-08-13%2000:10:00>

- **Descrição**: Filtra as observações de embarcações por um intervalo de tempo específico. Essa funcionalidade é útil para análises temporais. No exemplo, as observações entre meia-noite e 00:10 do dia 13 de agosto de 2024 são filtradas.

### 4. Retorno de Embarcação por Identificador Único ( GET )

- Para fazer essa consulta, também é necessário baixar o arquivo ```historico_acompanhamentos_24horas.csv``` e colocá-lo no mesmo diretório que o ```app.py```. Se isso não foi feito anteriormente, é necessário realizá-lo agora.

- **Rota**: <http://127.0.0.1:5000/vessel/vessel_id>

- **Exemplo**: <http://127.0.0.1:5000/vessel/IHS-AIS-205188000>

- **Descrição**: Esta funcionalidade permite retornar os dados de uma embarcação específica através de seu identificador único. É útil para acessar rapidamente as informações detalhadas de uma embarcação.

## Formato de dados AIS utilizado no Tais

A aplicação utiliza o formato JSON para representar as informações de rastreamento de embarcações em tempo real. Abaixo está a estrutura de dados AIS processada, que contém dados detalhados sobre a posição das embarcações, incluindo coordenadas geográficas, velocidade, rumo e outros parâmetros relevantes.

### Organização das pastas

Os dados de rastreamento das embarcações são organizados em uma estrutura de pastas dentro do diretório ```data/cinematicas/```. Cada embarcação ou sistema de rastreamento tem uma subpasta específica, que é nomeada com um identificador único. Este identificador pode ser o nome da fonte de dados ou um código único, como ```ENTTM-RAD--<ID>```, ```OPENAV-FUN--<ID>```, ou outros, dependendo da origem dos dados. Dentro de cada subpasta, os dados da embarcação são armazenados em arquivos JSON nomeados com base em um timestamp, representando o momento exato em que os dados foram registrados.

### Processamento dos dados CSV

Além dos dados JSON, a aplicação utiliza o arquivo ```historico_acompanhamentos_24horas.csv```, que contém dados históricos de rastreamento. O CSV é lido e processado, permitindo a consulta de dados filtrados por timestamp ou ID da embarcação. Quando necessário, o arquivo é ordenado para garantir que os dados sejam manipulados de forma cronológica.

#### Campos do CSV

O arquivo ```historico_acompanhamentos_24horas.csv``` possui as seguintes colunas principais:

| **Coluna**   | **Descrição**                                  |
|--------------|------------------------------------------------|
| `vesselId`   | Identificador único da embarcação              |
| `lat`        | Latitude da posição da embarcação              |
| `long`       | Longitude da posição da embarcação             |
| `timestamp`  | Carimbo de data e hora do evento (em formato `YYYY-MM-DD HH:MM:SS`) |

### Descrição dos campos JSON

O formato dos dados utilizados segue a seguinte estrutura:

```json
{
  "fonte": "<Fonte dos Dados>",
  "timestamp": "<Carimbo de data e hora do registro>",
  "perdido": <Booleano que indica se os dados estão perdidos>,
  "cinematica": {
    "timestamp": "<Carimbo de data e hora do movimento>",
    "posicao": {
      "geo": {
        "lat": <Latitude da posição da embarcação>,
        "lng": <Longitude da posição da embarcação>
      }
    },
    "rumo": {
      "fundo": <Rumo da embarcação em graus>
    },
    "velocidade": {
      "fundo": <Velocidade da embarcação em nós>
    },
    "estimarPosicao": <Booleano que indica se a posição foi estimada>
  },
  "identificacao": {
    "identificador": "<Identificador único da embarcação>"
  },
  "origem": "<Fonte do dado>",
  "subOrigem": {
    "nome": "<Nome da suborigem>",
    "codigo": "<Código da suborigem>"
  },
  "descricaoOrigem": "<Descrição da origem>",
  "sensores": {},
  "classificacao": {
    "tipoPrioritaria": "<Tipo de prioridade da embarcação>",
    "voluntaria": {
      "sidc": "<SIDC da embarcação>",
      "ocorrencia": "<Timestamp da ocorrência>"
    },
    "sidc": "<SIDC da embarcação>",
    "dimensao": {
      "descricao": "<Descrição da dimensão da embarcação>",
      "codigo": "<Código de classificação da embarcação>"
    },
    "hostilidade": {
      "descricao": "<Descrição do status de hostilidade>",
      "codigo": "<Código do status de hostilidade>"
    }
  },
  "uuid": "<UUID do dado>",
  "participanteFusao": <Booleano que indica se a embarcação participa de fusão de dados>,
  "emOperacao": <Booleano que indica se a embarcação está em operação>,
  "guid": "<GUID único do dado>"
}
```

## Observações

- Os dados utilizados pela API são lidos de arquivos JSON e CSV armazenados localmente.

- Certifique-se de que os arquivos necessários estejam no diretório correto antes de executar as funcionalidades da API.
