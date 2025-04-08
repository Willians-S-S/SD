# Trabalho 4 – Sistemas Distribuídos

> Arquitetura Mestre-Escravo com Threads, Middleware, Paralelismo e Docker

## 💡 Objetivo

Implementar um sistema distribuído em Java puro com a seguinte arquitetura:

- **Cliente (Java com GUI)** envia um `.txt` com letras e números.
- **Mestre (Java Server)** recebe o texto, dispara duas threads paralelas.
- Cada thread se comunica com um **escravo** para contar letras ou números.
- Resultado final é combinado e devolvido ao cliente.

---

## 🧱 Estrutura do Projeto

```bash

Trabalho-4/
├── Cliente/                # GUI em Java (Swing/JavaFX)
│   ├── tela_cliente.java
│   ├── cliente_http.java
├── Mestre/
│   ├── MestreServer.java
│   ├── WorkerThread.java
│   ├── Dockerfile
├── EscravoLetras/
│   ├── EscravoLetras.java
│   ├── Dockerfile
├── EscravoNumeros/
│   ├── EscravoNumeros.java
│   ├── Dockerfile
├── docker-compose.yml

```

## 🚀 Como Executar

### Pré-requisitos

- Docker e Docker Compose instalados
- Java instalado para compilar e executar o cliente localmente

### 1. Subir os containers

Dentro da raiz do projeto:

```bash

docker-compose up --build

```

Isso vai levantar:

- mestre na porta 8080

- escravo1 na porta 8001

- escravo2 na porta 8002

### 2. Rodar o Cliente

Compile e execute a GUI localmente (fora do Docker):

```bash

cd Cliente
javac tela_cliente.java cliente_http.java
java tela_cliente

```

### Na GUI, selecione o .txt com letras e números e envie. O sistema irá:

- Enviar o arquivo para o mestre.

 -O mestre envia texto para:

    escravo1 → conta letras

    escravo2 → conta números

    Resultado final aparece na tela.


### Tecnologias Usadas
    -Java 17

    -Java Swing

    -Java HTTP Server (com.sun.net.httpserver)

    -Docker

    -Docker Compose

Os containers se comunicam pela rede Docker interna usando os nomes:

http://escravo1:8001/letras

http://escravo2:8002/numeros

O cliente pode rodar em outra máquina se apontar para o IP do mestre.
