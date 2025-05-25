# config.py

HOST = '127.0.0.1'  # localhost

# Configurações do Source
SOURCE_LISTEN_PORT = 9000 # Porta onde o Source escuta os resultados finais
SOURCE_PREP_TIME = 0.05
SOURCE_COMPILE_TIME = 0.03
SOURCE_TARGET_LB1_HOST = HOST
SOURCE_TARGET_LB1_PORT = 9001

# Configurações do LoadBalancer1 (LB1)
LB1_LISTEN_PORT = 9001
LB1_PROC_TIME = 0.02
LB1_TARGET_SERVICE_HOSTS = [HOST, HOST]
LB1_TARGET_SERVICE_PORTS = [9002, 9003] # Service1.1, Service1.2
LB1_NAME_TAG = "LoadBalancer1_Nó02" # Para logging e timestamps

# Configurações do Service1.1 (S1_1)
S1_1_LISTEN_PORT = 9002
S1_1_NAME_TAG = "Service1.1_Nó02"
S1_1_PROC_TIME = 0.1
S1_1_TRANSIT_TIME_TO_NEXT = 0.01 # T3 parcial
S1_1_NEXT_TARGET_HOST = HOST
S1_1_NEXT_TARGET_PORT = 9004 # LB2

# Configurações do Service1.2 (S1_2)
S1_2_LISTEN_PORT = 9003
S1_2_NAME_TAG = "Service1.2_Nó02"
S1_2_PROC_TIME = 0.09
S1_2_TRANSIT_TIME_TO_NEXT = 0.01 # T3 parcial
S1_2_NEXT_TARGET_HOST = HOST
S1_2_NEXT_TARGET_PORT = 9004 # LB2

# Configurações do LoadBalancer2 (LB2)
LB2_LISTEN_PORT = 9004
LB2_PROC_TIME = 0.02
LB2_TARGET_SERVICE_HOSTS = [HOST, HOST]
LB2_TARGET_SERVICE_PORTS = [9005, 9006] # Service2.1, Service2.2
LB2_NAME_TAG = "LoadBalancer2_Nó03" # Para logging e timestamps

# Configurações do Service2.1 (S2_1)
S2_1_LISTEN_PORT = 9005
S2_1_NAME_TAG = "Service2.1_Nó03"
S2_1_PROC_TIME = 0.15
S2_1_TRANSIT_TIME_TO_NEXT = 0.01 # T5 parcial
S2_1_NEXT_TARGET_HOST = HOST # Source
S2_1_NEXT_TARGET_PORT = SOURCE_LISTEN_PORT # Source (onde escuta resultados)

# Configurações do Service2.2 (S2_2)
S2_2_LISTEN_PORT = 9006
S2_2_NAME_TAG = "Service2.2_Nó03"
S2_2_PROC_TIME = 0.16
S2_2_TRANSIT_TIME_TO_NEXT = 0.01 # T5 parcial
S2_2_NEXT_TARGET_HOST = HOST # Source
S2_2_NEXT_TARGET_PORT = SOURCE_LISTEN_PORT # Source (onde escuta resultados)

# Simulação
REQUEST_COUNT = 3 # Número de mensagens que o Source enviará