# Sistema de Carga com IA nos Consumidores

Este projeto implementa um sistema distribuído em containers que gera e processa mensagens usando RabbitMQ como broker. O sistema consiste em:

```
sistema-carga-ia/
├── docker-compose.yml          # Orquestração dos containers
├── .env                        # Variáveis de ambiente
├── README.md                   # Documentação do projeto
├── generator/                  # Serviço gerador de mensagens
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app.py                  # Aplicação principal
│   └── images/                 # Imagens para envio
│       ├── faces/              # Rostos para análise de sentimento
│       └── teams/              # Brasões de times de futebol
├── consumer_face/              # Consumidor 1: análise de sentimento
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app.py                  # Aplicação com IA 1
└── consumer_team/              # Consumidor 2: identificação de times
    ├── Dockerfile
    ├── requirements.txt
    └── app.py                  # Aplicação com IA 2
```

## Componentes

1. **Gerador de Mensagens**:
   
   - Envia 5+ mensagens por segundo para o RabbitMQ
   - Alterna entre imagens de rostos e brasões de times
   - Utiliza routing keys apropriadas ("face" ou "team")

2. **RabbitMQ**:
   
   - Exchange tipo topic configurado
   - Interface de administração habilitada na porta 15672

3. **Consumidor 1 (Faces)**:
   
   - Consome mensagens com routing key "face"
   - Usa IA para análise de sentimento facial
   - Processamento deliberadamente lento

4. **Consumidor 2 (Times)**:
   
   - Consome mensagens com routing key "team"
   - Usa IA para identificação de brasões de times
   - Processamento deliberadamente lento

## Network Docker

Todos os serviços estão conectados na mesma rede Docker chamada `rabbitmq-ai-network`.

## Como Executar o Projeto

1. **Construir e Iniciar Containers**:
   
   ```bash
   docker-compose up --build
   ```

2. **Monitorar o Sistema**:
   
   - Acesse o painel do RabbitMQ: http://localhost:15672 (user: admin, pass: admin123)
   - Para observar os logs dos containers para ver os resultados das análises de IA, utilize o comando:
     
     ```bash
     docker-compose logs -f
     ```
