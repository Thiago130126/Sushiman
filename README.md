# Aplicação WEB do SUSHIMAN

## Execução do Código
### Para executar o código basta usar o comando: 
* docker compose up \
### Para ele buildar os containeres junto de executar o projeto, é só adicionar a flag --build:
* docker compose up --build \
### Para a execução não obstruir e ocupar o terminal, é só adicionar a flag -d:
* docker compose up -d --build

### Para encerrar o container:
* docker compose down

# Em desenvolvimento o projeto pode ser acessado pela rota localhost:8080


## Configuração

Configurei o settings.py do django já para usar o banco de dados criado no container docker. Configurei o nginx, fiz os dockerfiles do django e do next. Fiz o docker-compose do projeto em dois arquivos, .yml para ambiente de desenvolvimento e .prod.yml para ambiente de produção.
Comfigurei o sistema de logging do django para salvar e fazer rotação de arquivos de logs. Deixei pronto .env.examples com algumas explicações do que colocar em cada variável.
* Já deixei pronta a arquitetura de hierarquia de componentes com as pastas atoms, molecules, organisms e pages.
* Também deixei criado o app accounts que ficará responsável por lidar com o usuário


# GitHub

## Branch Main

A main está protegida de qualquer commit, para fazer um commit no repositório, na pasta do código, precisa criar umar nova branch com o comando git checkout -b 'nome'