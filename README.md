# TAIS APP

Tool for analisys of AIS data

## Execução do Servidor Back-End

### Para executar no ambiente de Desenvolvimento (DEV)

1. Execute o terminal
2. Vá para o diretório com o comando ```cd api```
3. Execute o comando ```docker-compose -f .\docker-compose.dev.yml build``` para gerar a imagem da máquina que irá rodar a API
4. Execute o comando  ```docker-compose -f .\docker-compose.dev.yml up``` para executar o container e rodar a aplicação. Após a execução do comando, deverá aparecer em um Log gerado pelo Flask, a URL em que a aplicação está rodando. Ex: <http://localhost:5000>

### Alternativamente para rodar a aplicação sem o encapsulamento do Docker

1. Execute o terminal
2. Vá para o diretório com o comando ```cd api/app```
3. Crie e ative a venv ```python -m venv venv``` e em seguida ```venv\Scripts\activate```
4. Instale as dependências executando o comando ```pip install -r requirements.txt```
5. Execute o comando ```python app.py``` para rodar a aplicação flask diretamente
6. Após a execução do comando, deverá aparecer em um Log gerado pelo Flask, a URL em que a aplicação está rodando. Ex: <http://localhost:5000>

### Instruções sobre a utilização da API

## 1. Visualização de Dados Processados ( GET )

 Rota: /api/data

 Descrição: Esta funcionalidade permite o acesso a dados processados em formato
JSON. Os dados podem ser utilizados para análise, visualização ou integração com
outras aplicações.

## 2. Mapa de Calor (Heatmap) ( GET )

 Rota: /api/heatmap

 Descrição: Permite a visualização de um mapa de calor baseado nos dados AIS
disponíveis. Este mapa de calor pode ser utilizado para identificar áreas de alta ou
baixa densidade de tráfego marítimo.

## 3. Filtragem por Intervalo de Tempo ( GET )

 Rota: <http://127.0.0.1:5000/timestamp/start/end>

 Exemplo: <http://127.0.0.1:5000/timestamp/2024-08-13%2000:00:00/2024->
08-13%2000:10:00

 Descrição: Oferece a capacidade de filtrar as observações das embarcações por um
intervalo de tempo específico. Essa funcionalidade é útil para análises temporais,
permitindo focar em períodos de interesse. O exemplo acima filtra as observações
compreendidas no intervalo do dia 13 de agosto entre meia-noite e meia-noite e dez

## 4. Retorno de Embarcação por Identificador Único ( GET )

 Rota: <http://127.0.0.1:5000/vessel/>

 Exemplo: <http://127.0.0.1:5000/vessel/IHS-AIS-232009709>

 Descrição: Esta funcionalidade permite retornar os dados de uma embarcação
específica através de seu identificador único. É útil para acessar rapidamente as
informações detalhadas de uma embarcação.

OBS: Os dados que servem a API estão sendo lidos de arquivos json armazenados localmente e de um arquivo csv também armazenado localmente.
