# config.py
import os

# --- CONFIGURAÇÕES GERAIS ---
IS_DOCKER_ENV = os.getenv('DOCKER_ENV', 'false').lower() == 'true'

HOST_CONFIG = {
    'source': 'source' if IS_DOCKER_ENV else '127.0.0.1',
    'lb1': 'lb1' if IS_DOCKER_ENV else '127.0.0.1',
    's1_1': 's1_1' if IS_DOCKER_ENV else '127.0.0.1',
    's1_2': 's1_2' if IS_DOCKER_ENV else '127.0.0.1',
    'lb2': 'lb2' if IS_DOCKER_ENV else '127.0.0.1',
    's2_1': 's2_1' if IS_DOCKER_ENV else '127.0.0.1',
    's2_2': 's2_2' if IS_DOCKER_ENV else '127.0.0.1',
    'localhost': '127.0.0.1',
    'bind_all': '0.0.0.0'
}

# --- CAMINHOS DO MODELO BERT ---
CAMINHO_MODELO_BERT_CONTAINER = "/app/bert_model_data"
CAMINHO_MODELO_BERT_HOST_PY = os.getenv("CAMINHO_MODELO_BERT_HOST_ENV", "./dummy_bert_model")

# --- Diretório de Logs ---
LOGS_DIR_CONTAINER = "/app/logs" # Usado pelo source.py para saber onde escrever o CSV

# --- Configurações do Source ---
SOURCE_NAME_TAG = os.getenv("SOURCE_NAME_TAG", "Source_Nó01")
SOURCE_LISTEN_PORT = int(os.getenv("SOURCE_LISTEN_PORT_CONTAINER", 9000))
SOURCE_PREP_TIME = float(os.getenv("SOURCE_PREP_TIME", 0.05))
SOURCE_COMPILE_TIME = float(os.getenv("SOURCE_COMPILE_TIME", 0.03))
SOURCE_TARGET_LB1_HOST = HOST_CONFIG['lb1'] # Nome do serviço Docker
SOURCE_TARGET_LB1_PORT = int(os.getenv("LB1_LISTEN_PORT", 9001))
# Valores do experimento, lidos do ambiente (que vem do .env via docker-compose)
REQUEST_COUNT = int(os.getenv("REQUEST_COUNT", 10)) # Default se não definido no .env
SOURCE_INTERVAL_BETWEEN_REQUESTS = float(os.getenv("SOURCE_INTERVAL_BETWEEN_REQUESTS", 0.5)) # Default

# --- Configurações dos LoadBalancers e Services (Defaults que os scripts usarão se args não forem passados) ---
# Os scripts (loadbalancer.py, service.py) são primariamente configurados por argumentos de linha de comando
# que são definidos no docker-compose.yml, que por sua vez pode usar variáveis do .env.
# Estas definições no config.py servem mais como fallback ou para clareza/referência.

LB1_NAME_TAG = os.getenv("LB1_NAME_TAG", "LoadBalancer1_Nó02")
LB1_LISTEN_PORT = int(os.getenv("LB1_LISTEN_PORT", 9001))
LB1_PROC_TIME = float(os.getenv("LB1_PROC_TIME", 0.02)) # Usado pelo --ptime arg

S1_1_NAME_TAG = os.getenv("S1_1_NAME_TAG", "Service1.1_Nó02")
S1_1_LISTEN_PORT = int(os.getenv("S1_1_LISTEN_PORT", 9002))
S1_1_PROC_TIME = float(os.getenv("S1_1_PROC_TIME", 0.1)) # Usado pelo --ptime_no_ia arg
S1_1_TRANSIT_TIME_TO_NEXT = float(os.getenv("S1_1_TRANSIT_TIME_TO_NEXT", 0.01))
S1_1_NEXT_TARGET_HOST = HOST_CONFIG['lb2']
S1_1_NEXT_TARGET_PORT = int(os.getenv("LB2_LISTEN_PORT", 9004))
S1_1_HAS_IA = False

S1_2_NAME_TAG = os.getenv("S1_2_NAME_TAG", "Service1.2_Nó02")
S1_2_LISTEN_PORT = int(os.getenv("S1_2_LISTEN_PORT", 9003))
S1_2_PROC_TIME = float(os.getenv("S1_2_PROC_TIME", 0.09)) # Usado pelo --ptime_no_ia arg
S1_2_TRANSIT_TIME_TO_NEXT = float(os.getenv("S1_2_TRANSIT_TIME_TO_NEXT", 0.01))
S1_2_NEXT_TARGET_HOST = HOST_CONFIG['lb2']
S1_2_NEXT_TARGET_PORT = int(os.getenv("LB2_LISTEN_PORT", 9004))
S1_2_HAS_IA = False

LB2_NAME_TAG = os.getenv("LB2_NAME_TAG", "LoadBalancer2_Nó03")
LB2_LISTEN_PORT = int(os.getenv("LB2_LISTEN_PORT", 9004))
LB2_PROC_TIME = float(os.getenv("LB2_PROC_TIME", 0.02)) # Usado pelo --ptime arg

# Service2.x Defaults (IA)
S2_DEFAULT_PROC_TIME_NO_IA = float(os.getenv("S2_PROC_TIME", 0.0)) # Usado pelo --ptime_no_ia arg
S2_DEFAULT_TRANSIT_TIME_TO_NEXT = float(os.getenv("S2_TRANSIT_TIME", 0.01))
S2_DEFAULT_BERT_MODEL_NAME = os.getenv("S2_BERT_MODEL_NAME", 'neuralmind/bert-large-portuguese-cased')
S2_DEFAULT_MODEL_PATH_DOCKER = CAMINHO_MODELO_BERT_CONTAINER
S2_DEFAULT_MODEL_PATH_LOCAL = CAMINHO_MODELO_BERT_HOST_PY
S2_DEFAULT_NUM_CLASSES = int(os.getenv("S2_NUM_CLASSES", 3))
S2_DEFAULT_MAX_LEN = int(os.getenv("S2_MAX_LEN", 180))
S2_DEFAULT_STATE_DICT_FILENAME = os.getenv("S2_STATE_DICT_FILENAME", "") # Lê do .env

S2_1_NAME_TAG = os.getenv("S2_1_NAME_TAG", "Service2.1_Nó03")
S2_1_LISTEN_PORT = int(os.getenv("S2_1_LISTEN_PORT", 9005))
S2_1_NEXT_TARGET_HOST = HOST_CONFIG['source']
S2_1_NEXT_TARGET_PORT = SOURCE_LISTEN_PORT
S2_1_HAS_IA = True

S2_2_NAME_TAG = os.getenv("S2_2_NAME_TAG", "Service2.2_Nó03")
S2_2_LISTEN_PORT = int(os.getenv("S2_2_LISTEN_PORT", 9006))
S2_2_NEXT_TARGET_HOST = HOST_CONFIG['source']
S2_2_NEXT_TARGET_PORT = SOURCE_LISTEN_PORT
S2_2_HAS_IA = True

# Amostras de texto para IA
SAMPLE_IA_TEXTS = [
    "Eu adorei este filme, os atores foram incríveis e a história me prendeu do início ao fim!",
    "Que decepção, esperava muito mais deste produto, não recomendo a ninguém.",
    "O atendimento no restaurante foi péssimo, demorou horas e a comida veio fria.",
    "Este produto superou minhas expectativas, excelente qualidade!",
    "O serviço ao cliente foi rápido e eficiente.",
    "Não gostei da interface, achei confusa e pouco intuitiva.",
    "A comida estava razoável, mas o preço um pouco alto pelo que foi oferecido.",
    "Experiência incrível, recomendo a todos os meus amigos!",
    "Demorou muito para chegar e veio com defeito.",
    "O filme tem um roteiro previsível, mas boas atuações."
]

# Nomes de serviço para uso no docker-compose.yml (para os --targets e --next_host)
# Estes são os nomes que o Docker DNS usará.
DOCKER_SERVICE_NAMES = {
    'source': os.getenv("SOURCE_SERVICE_NAME", "source"),
    'lb1': os.getenv("LB1_SERVICE_NAME", "lb1"),
    's1_1': os.getenv("S1_1_SERVICE_NAME", "s1_1"),
    's1_2': os.getenv("S1_2_SERVICE_NAME", "s1_2"),
    'lb2': os.getenv("LB2_SERVICE_NAME", "lb2"),
    's2_1': os.getenv("S2_1_SERVICE_NAME", "s2_1"),
    's2_2': os.getenv("S2_2_SERVICE_NAME", "s2_2"),
}