# TAIS APP
Tool for analisys of AIS data

## Execução do Servidor Back-End

### Para executar no ambiente de Desenvolvimento (DEV)

1. Execute o terminal
2. Vá para o diretório com o comando ```cd api ```
3. (opcional) Verifique se as variáveis de ambiente no arquivo `entrypoint.sh` estão corretas, caso queira testar outra Base de Dados.
4. Execute o comando ```docker-compose -f .\docker-compose.dev.yml build``` para gerar a imagem da máquina que irá rodar a API
5. Execute o comando  ```docker-compose -f .\docker-compose.dev.yml up``` para executar o comtainer e rodar a aplicação. Após a execução do comando, deverá aparecer em um Log gerado pelo Flask, a URL em que a aplicação está rodando. Ex: http://localhost:5000

Detalhes:
* Toda vez que o build for executado na máquina no ambiente de desenvolvimento, o script chamado init.sql irá executar. Fazendo com que a tabela utilizada na aplicação seja criada junto com a inserção de alguns dados nessa tabela. Para que seja possivel utilizar a aplicação sem ocorrer problemas com o Banco de Dados.

### Para executar no ambiente de Produção (PROD)

1. Execute o terminal
2. Vá para o diretório com o comando ```cd api ```
3. Verifique se as variáveis de ambiente no arquivo `entrypoint.sh` estão corretas e se estão apontando para os dados de produção corretamente, caso não esteja, altere-as.
4. Execute o comando ```docker-compose -f .\docker-compose.prod.yml build``` para gerar a imagem da máquina que irá rodar a API
5. Execute o comando  ```docker-compose -f .\docker-compose.prod.yml up``` para executar o comtainer e rodar a aplicação. Após a execução do comando, deverá aparecer em um Log gerado pelo Flask, a URL em que a aplicação está rodando. Ex: http://localhost:5000

Detalhes:
* O ideal para alterar variáveis de ambiente em produção é dentro do próprio servidor, para que os dados não fiquem expostos no Repositório.
* Este ambiente não executa um script SQL para criar os dados, pois o mesmo deverá apontar para a Base de Dados já existente dentro do Servidor.
* É necessário ter configurado o NGINX para fazer a utilização do PROXY no Servidor.

## Execução da Interface Front-End

### Para executar no ambiente de Desenvolvimento (DEV)
1. Execute o terminal
2. Vá para o diretório com o comando ```cd front ```
3. Verifique se as variáveis de ambiente no arquivo `entrypoint.sh` estão corretas, caso tenha alterado a porta em que a aplicação do Servidor Back-End está rodando.
4. Execute o comando ```docker-compose -f .\docker-compose.dev.yml build``` para gerar a imagem da máquina que irá rodar o Servidor
5. Execute o comando  ```docker-compose -f .\docker-compose.dev.yml up``` para executar o comtainer e rodar a aplicação. Após a execução do comando, deverá aparecer os Logs gerados pelo npm ao executar a aplicação, e deverá rodar na url http://localhost:[PORTA_DEFINIDA_NO_FRONTEND].

### Para executar no ambiente de Produção (PROD)

1. Execute o terminal
2. Vá para o diretório com o comando ```cd front ```
3. Verifique se as variáveis de ambiente no arquivo `entrypoint.sh` estão corretas, caso tenha alterado a porta em que a aplicação do Servidor Back-End está rodando.
4. Execute o comando ```docker-compose -f .\docker-compose.prod.yml build``` para gerar a imagem da máquina que irá rodar o Servidor
5. Execute o comando  ```docker-compose -f .\docker-compose.prod.yml up``` para executar o comtainer e rodar a aplicação. Após a execução do comando, deverá aparecer os Logs gerados pelo npm ao executar a aplicação, e deverá rodar na url http://localhost:[PORTA_DEFINIDA_NO_FRONTEND].

Detalhes:
* O ideal para alterar variáveis de ambiente em produção é dentro do próprio servidor, para que os dados não fiquem expostos no Repositório.
* É necessário ter configurado o NGINX para fazer a utilização do PROXY no Servidor.
* Após a execução da aplicação no Servidor, a mesma deve ser exibida na url https://dal.eic.cefet-rj.br/tais
