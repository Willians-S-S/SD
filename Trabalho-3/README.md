Editor de Imagens com Flask e Tkinter

Este projeto consiste em um sistema de três camadas que permite o upload de imagens através de uma interface gráfica em Tkinter, a aplicação de filtros em um servidor Flask e o armazenamento das imagens processadas e seus metadados em um banco de dados SQLite.

Funcionalidades

* Upload de imagens pela interface Tkinter

* Envio da imagem para um servidor Flask

* Aplicação de filtro (exemplo: inversão de cores)

* Exibição da imagem original e processada

* Armazenamento das imagens em disco

* Registro dos metadados (nome do arquivo, filtro aplicado e data/hora) em SQLite

Como Executar

1. Clonar o Repositório

```bash

git clone https://github.com/seu-repositorio/editor-imagens.git
cd editor-imagens

```
2. Instalar Dependências

Certifique-se de ter o Python instalado e execute:
```bash

pip install flask pillow requests

```
3. Iniciar o Servidor Flask

```bash

python server.py

```

O servidor será iniciado na porta 5000.

4. Executar a Interface Gráfica Tkinter

```bash

python client.py

```

A interface será aberta para que você possa selecionar e enviar uma imagem.

Estrutura do Projeto

```bash

editor-imagens/
│-- server.py         # Servidor Flask
│-- client.py         # Interface Tkinter
│-- images.db         # Banco de dados SQLite
│-- uploads/         # Diretório de imagens originais
│-- processed/       # Diretório de imagens processadas
│-- README.md        # Documentação

```
