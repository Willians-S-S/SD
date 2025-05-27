# Trabalho Final parte 1 

Este projeto simula um sistema distribuído, modelando um fluxo de processamento de dados através de múltiplos nós: uma fonte (Source), balanceadores de carga (Load Balancers) e serviços de processamento (Services). A comunicação entre os nós é realizada via sockets TCP/IP, e o sistema é orquestrado para iniciar e gerenciar todos os componentes a partir de um único script (`source.py`).

O simulador também implementa a medição de tempos em diferentes estágios do processamento, calculando métricas T1 a T5 para cada requisição, conforme um modelo de pipeline.

## Funcionalidades Principais

* **Simulação de Arquitetura Distribuída:** Modela um sistema com nós distintos (Source, Load Balancer, Service).
* **Comunicação via Sockets:** Todos os componentes se comunicam usando sockets TCP/IP.
* **Orquestração Centralizada:** O script `source.py` atua como orquestrador, iniciando todos os outros nós (load balancers e serviços) como subprocessos.
* **Balanceamento de Carga:** Os Load Balancers distribuem as requisições para os serviços usando uma estratégia Round Robin.
* **Simulação de Tempo:**
    * Simula tempos de processamento em cada nó.
    * Simula tempos de trânsito da rede entre os nós.
    * Coleta timestamps em pontos chave (M1-M6) do fluxo.
    * Calcula e exibe as durações T1, T2, T3, T4 e T5 para cada requisição processada.
* **Configuração Flexível:** Parâmetros como hosts, portas, tempos de processamento e de trânsito são configuráveis através do arquivo `config.py`.
* **Modularidade:** O código é organizado em módulos para cada tipo de componente e utilitários.

## Estrutura de Diretórios

```
.
├── config.py           # Arquivo de configuração central (portas, hosts, tempos)
├── source.py           # Nó Source, orquestrador da simulação e coletor de resultados
├── loadbalancer.py     # Lógica do nó Load Balancer
├── service.py          # Lógica do nó Service
├── socket_utils.py     # Funções utilitárias para comunicação via socket
└── README.md           # Este arquivo
```

## Pré-requisitos

* Python 3.x (o projeto utiliza apenas a biblioteca padrão do Python).

## Configuração

Todas as configurações do sistema, como:
* Endereços de host e portas para cada nó.
* Tempos de processamento simulados para cada tipo de nó.
* Tempos de trânsito simulados entre os nós.
* Número de requisições a serem geradas pelo Source.

Podem ser ajustadas no arquivo `config.py`. Certifique-se de que as portas configuradas estejam livres em sua máquina.


## Como Executar

1.  **Certifique-se de que todos os arquivos Python (`source.py`, `loadbalancer.py`, `service.py`, `socket_utils.py`, `config.py`) estejam no mesmo diretório.**
2.  Abra um terminal ou prompt de comando.
3.  Navegue até o diretório onde os arquivos do projeto estão localizados.
4.  Execute o script `source.py`. Ele se encarregará de iniciar todos os outros componentes como subprocessos e, em seguida, iniciar a simulação.

    ```bash
    python source.py
    ```

O script `source.py` primeiro lançará os processos dos serviços e load balancers na ordem correta (serviços mais distantes primeiro, depois seus LBs, e assim por diante) e, após uma breve pausa para garantir que eles estejam escutando, o Source começará a enviar as requisições.

## Saída Esperada

Ao executar o `source.py`, você verá no console:
* Logs indicando o início de cada nó (serviço e load balancer) como subprocessos.
* Logs de cada nó individual (Source, Load Balancer, Service) detalhando:
    * Recebimento de requisições.
    * Tempos de processamento simulados.
    * Encaminhamento de dados para o próximo nó.
    * Envio e recebimento de resultados finais.
* Ao final da simulação, o `Source` imprimirá:
    * Um resumo dos tempos (T1, T2, T3, T4, T5) para cada requisição processada.
    * O tempo total de processamento para cada requisição (M6 - M1).
    * Uma soma de verificação (T1+T2+T3+T4+T5).
    * Status final da compilação e validação dos resultados.
    * O tempo médio total por requisição.
* Logs indicando o encerramento dos nós subprocessos.

A saída dos diferentes processos será intercalada no console principal, pois todos compartilham o mesmo stdout/stderr por padrão.
