#!/bin/bash

# --- Configuração ---
REQUEST_COUNTS=(20 50 100 150 200 250 300)
# NUM_ACTIVE_SERVICES define o número total de serviços S1/S2 na pipeline
NUM_ACTIVE_SERVICES_CONFIGS=(1 2 3 4)

# Diretórios de log e resultados
LOG_DIR_HOST="./logs"
RESULTS_ARCHIVE_DIR_HOST="./results_archive"
METRICS_TEMP_DIR_HOST="./metrics" # Usado pela saída padrão do parse_source.py

# Garante que os diretórios existam
mkdir -p "$LOG_DIR_HOST"
mkdir -p "$RESULTS_ARCHIVE_DIR_HOST"
mkdir -p "$METRICS_TEMP_DIR_HOST"

# --- Cria/Atualiza o arquivo .env para o Docker Compose ---
cat << EOF > .env
# Arquivo .env do Runner de Experimentos
DOCKER_ENV=true
SOURCE_RUN_MODE=experiment # Para execuções automatizadas

# Portas para os serviços (garanta que sejam únicas)
SOURCE_LISTEN_PORT_CONTAINER=9000
SOURCE_LISTEN_PORT_HOST=9000

LB1_LISTEN_PORT=9001
S1_1_LISTEN_PORT=9002
S1_2_LISTEN_PORT=9003 # Ativo apenas para 2+ serviços

LB2_LISTEN_PORT=9004  # Ativo apenas para 3+ serviços
S2_1_LISTEN_PORT=9005 # Ativo apenas para 3+ serviços
S2_2_LISTEN_PORT=9006 # Ativo apenas para 4 serviços

# Nomes dos Serviços (devem corresponder aos nomes no compose)
SOURCE_SERVICE_NAME=source
LB1_SERVICE_NAME=lb1
S1_1_SERVICE_NAME=s1_1
S1_2_SERVICE_NAME=s1_2
LB2_SERVICE_NAME=lb2
S2_1_SERVICE_NAME=s2_1
S2_2_SERVICE_NAME=s2_2

# Tempos de Processamento Padrão
SOURCE_PREP_TIME=0.05
SOURCE_COMPILE_TIME=0.03
LB1_PROC_TIME=0.02
S1_1_PROC_TIME=0.1
S1_2_PROC_TIME=0.09
LB2_PROC_TIME=0.02
S2_PROC_TIME=0.0 # Para serviços com IA, ptime_no_ia geralmente é 0

S1_1_TRANSIT_TIME_TO_NEXT=0.01
S1_2_TRANSIT_TIME_TO_NEXT=0.01
S2_TRANSIT_TIME=0.01

# Configuração do Modelo BERT
CAMINHO_MODELO_BERT_HOST_ENV=./dummy_bert_model # Use um modelo dummy se não tiver o real
CAMINHO_MODELO_BERT_CONTAINER=/app/bert_model_data
S2_BERT_MODEL_NAME=neuralmind/bert-base-portuguese-cased # Modelo menor para testes mais rápidos
S2_NUM_CLASSES=3
S2_MAX_LEN=180
S2_STATE_DICT_FILENAME=

# Intervalo padrão entre requisições do Source
SOURCE_INTERVAL_BETWEEN_REQUESTS=0.5
EOF

echo "INFO: Arquivo .env gerado para o Docker Compose."

# --- Loop Principal do Experimento ---
for num_active_services in "${NUM_ACTIVE_SERVICES_CONFIGS[@]}"; do
  echo "INFO: Configurando para $num_active_services serviços S1/S2 ativos na pipeline."

  PROFILE_ARGS_LIST=() # Array para os perfis
  # Variáveis para configurar os comandos dos serviços via .env
  EXPERIMENT_LB1_TARGETS=""

  EXPERIMENT_S1_1_NEXT_HOST_CMD_ARG=""
  EXPERIMENT_S1_1_NEXT_PORT_CMD_ARG=""
  EXPERIMENT_S1_1_IS_FINAL_CMD_FLAG=""
  EXPERIMENT_S1_1_HAS_IA_CMD_FLAG="" # s1_1 nunca tem IA nestes cenários

  S1_2_NEXT_HOST_CMD_ARG=""
  S1_2_NEXT_PORT_CMD_ARG=""
  S1_2_IS_FINAL_CMD_FLAG=""
  S1_2_HAS_IA_CMD_FLAG="" # s1_2 nunca tem IA nestes cenários

  EXPERIMENT_LB2_TARGETS=""

  case $num_active_services in
    1)
      # Pipeline: source -> lb1 -> s1_1 (final, sem IA) -> source
      echo "  Pipeline: source -> lb1 -> s1_1 (final, sem IA) -> source"
      # Nenhum perfil extra necessário, s1_1 está sempre ativo por padrão com lb1
      EXPERIMENT_LB1_TARGETS="\${S1_1_SERVICE_NAME}:\${S1_1_LISTEN_PORT}"
      
      EXPERIMENT_S1_1_NEXT_HOST_CMD_ARG="--next_host \${SOURCE_SERVICE_NAME}"
      EXPERIMENT_S1_1_NEXT_PORT_CMD_ARG="--next_port \${SOURCE_LISTEN_PORT_CONTAINER}"
      EXPERIMENT_S1_1_IS_FINAL_CMD_FLAG="--is_final"
      # EXPERIMENT_S1_1_HAS_IA_CMD_FLAG permanece vazio (sem IA)
      ;;
    2)
      # Pipeline: source -> lb1(target s1_1) -> s1_1 (sem IA) -> s1_2 (final, sem IA) -> source
      echo "  Pipeline: source -> lb1 (alvo s1_1) -> s1_1 (sem IA) -> s1_2 (final, sem IA) -> source"
      PROFILE_ARGS_LIST+=("s1_2_active") # Ativa s1_2
      EXPERIMENT_LB1_TARGETS="\${S1_1_SERVICE_NAME}:\${S1_1_LISTEN_PORT}" # LB1 só conhece s1_1
      
      EXPERIMENT_S1_1_NEXT_HOST_CMD_ARG="--next_host \${S1_2_SERVICE_NAME}"
      EXPERIMENT_S1_1_NEXT_PORT_CMD_ARG="--next_port \${S1_2_LISTEN_PORT}"
      EXPERIMENT_S1_1_IS_FINAL_CMD_FLAG="" # s1_1 não é final

      # Configuração do s1_2 (ativo devido ao perfil)
      S1_2_NEXT_HOST_CMD_ARG="--next_host \${SOURCE_SERVICE_NAME}"
      S1_2_NEXT_PORT_CMD_ARG="--next_port \${SOURCE_LISTEN_PORT_CONTAINER}"
      S1_2_IS_FINAL_CMD_FLAG="--is_final"
      # S1_2_HAS_IA_CMD_FLAG permanece vazio
      ;;
    3)
      # Pipeline: source -> lb1(s1_1, s1_2) -> s1_x (sem IA) -> lb2(s2_1) -> s2_1 (final, com IA) -> source
      echo "  Pipeline: source -> lb1(alvos s1_1,s1_2) -> s1_x(sem IA) -> lb2(alvo s2_1) -> s2_1 (final, com IA) -> source"
      PROFILE_ARGS_LIST+=("s1_2_active" "lb2_s2_1_active") # Ativa s1_2, lb2, e s2_1
      EXPERIMENT_LB1_TARGETS="\${S1_1_SERVICE_NAME}:\${S1_1_LISTEN_PORT},\${S1_2_SERVICE_NAME}:\${S1_2_LISTEN_PORT}"
      
      # Configuração do s1_1
      EXPERIMENT_S1_1_NEXT_HOST_CMD_ARG="--next_host \${LB2_SERVICE_NAME}"
      EXPERIMENT_S1_1_NEXT_PORT_CMD_ARG="--next_port \${LB2_LISTEN_PORT}"
      EXPERIMENT_S1_1_IS_FINAL_CMD_FLAG=""

      # Configuração do s1_2 (ativo)
      S1_2_NEXT_HOST_CMD_ARG="--next_host \${LB2_SERVICE_NAME}"
      S1_2_NEXT_PORT_CMD_ARG="--next_port \${LB2_LISTEN_PORT}"
      S1_2_IS_FINAL_CMD_FLAG=""

      # Configuração do lb2 (ativo)
      EXPERIMENT_LB2_TARGETS="\${S2_1_SERVICE_NAME}:\${S2_1_LISTEN_PORT}"
      # s2_1 é configurado no docker-compose.yml para ser final e ter IA quando seu perfil está ativo
      ;;
    4)
      # Pipeline: source -> lb1(s1_1,s1_2) -> s1_x(sem IA) -> lb2(s2_1,s2_2) -> s2_x (final, com IA) -> source
      echo "  Pipeline: source -> lb1(s1_1,s1_2) -> s1_x(sem IA) -> lb2(s2_1,s2_2) -> s2_x (final, com IA) -> source"
      PROFILE_ARGS_LIST+=("s1_2_active" "lb2_s2_1_active" "s2_2_active") # Ativa s1_2, lb2, s2_1, e s2_2
      EXPERIMENT_LB1_TARGETS="\${S1_1_SERVICE_NAME}:\${S1_1_LISTEN_PORT},\${S1_2_SERVICE_NAME}:\${S1_2_LISTEN_PORT}"

      # Configuração do s1_1
      EXPERIMENT_S1_1_NEXT_HOST_CMD_ARG="--next_host \${LB2_SERVICE_NAME}"
      EXPERIMENT_S1_1_NEXT_PORT_CMD_ARG="--next_port \${LB2_LISTEN_PORT}"
      EXPERIMENT_S1_1_IS_FINAL_CMD_FLAG=""

      # Configuração do s1_2 (ativo)
      S1_2_NEXT_HOST_CMD_ARG="--next_host \${LB2_SERVICE_NAME}"
      S1_2_NEXT_PORT_CMD_ARG="--next_port \${LB2_LISTEN_PORT}"
      S1_2_IS_FINAL_CMD_FLAG=""

      # Configuração do lb2 (ativo)
      EXPERIMENT_LB2_TARGETS="\${S2_1_SERVICE_NAME}:\${S2_1_LISTEN_PORT},\${S2_2_SERVICE_NAME}:\${S2_2_LISTEN_PORT}"
      # s2_1 e s2_2 são configurados no docker-compose.yml para serem finais e terem IA quando seus perfis estão ativos
      ;;
    *)
      echo "ERRO: Número de serviços ativos não suportado: $num_active_services"
      continue # Pula para a próxima iteração de num_active_services
      ;;
  esac

  # Converte array de perfis para string para o comando docker-compose
  PROFILE_ARGS_STRING=""
  for profile in "${PROFILE_ARGS_LIST[@]}"; do
    PROFILE_ARGS_STRING+="--profile $profile "
  done

  # Remove configurações dinâmicas anteriores do .env e adiciona as novas
  sed -i '/^EXPERIMENT_LB1_TARGETS=/d' .env
  sed -i '/^EXPERIMENT_S1_1_NEXT_HOST_CMD_ARG=/d' .env
  sed -i '/^EXPERIMENT_S1_1_NEXT_PORT_CMD_ARG=/d' .env
  sed -i '/^EXPERIMENT_S1_1_IS_FINAL_CMD_FLAG=/d' .env
  sed -i '/^EXPERIMENT_S1_1_HAS_IA_CMD_FLAG=/d' .env
  sed -i '/^S1_2_NEXT_HOST_CMD_ARG=/d' .env
  sed -i '/^S1_2_NEXT_PORT_CMD_ARG=/d' .env
  sed -i '/^S1_2_IS_FINAL_CMD_FLAG=/d' .env
  sed -i '/^S1_2_HAS_IA_CMD_FLAG=/d' .env
  sed -i '/^EXPERIMENT_LB2_TARGETS=/d' .env

  echo "EXPERIMENT_LB1_TARGETS=$EXPERIMENT_LB1_TARGETS" >> .env
  echo "EXPERIMENT_S1_1_NEXT_HOST_CMD_ARG=$EXPERIMENT_S1_1_NEXT_HOST_CMD_ARG" >> .env
  echo "EXPERIMENT_S1_1_NEXT_PORT_CMD_ARG=$EXPERIMENT_S1_1_NEXT_PORT_CMD_ARG" >> .env
  echo "EXPERIMENT_S1_1_IS_FINAL_CMD_FLAG=$EXPERIMENT_S1_1_IS_FINAL_CMD_FLAG" >> .env
  echo "EXPERIMENT_S1_1_HAS_IA_CMD_FLAG=$EXPERIMENT_S1_1_HAS_IA_CMD_FLAG" >> .env
  
  echo "S1_2_NEXT_HOST_CMD_ARG=$S1_2_NEXT_HOST_CMD_ARG" >> .env
  echo "S1_2_NEXT_PORT_CMD_ARG=$S1_2_NEXT_PORT_CMD_ARG" >> .env
  echo "S1_2_IS_FINAL_CMD_FLAG=$S1_2_IS_FINAL_CMD_FLAG" >> .env
  echo "S1_2_HAS_IA_CMD_FLAG=$S1_2_HAS_IA_CMD_FLAG" >> .env

  echo "EXPERIMENT_LB2_TARGETS=$EXPERIMENT_LB2_TARGETS" >> .env
  
  echo "INFO: EXPERIMENT_LB1_TARGETS=$EXPERIMENT_LB1_TARGETS"
  echo "INFO: EXPERIMENT_S1_1_NEXT_HOST_CMD_ARG=$EXPERIMENT_S1_1_NEXT_HOST_CMD_ARG"
  echo "INFO: EXPERIMENT_S1_1_NEXT_PORT_CMD_ARG=$EXPERIMENT_S1_1_NEXT_PORT_CMD_ARG"
  echo "INFO: EXPERIMENT_S1_1_IS_FINAL_CMD_FLAG=$EXPERIMENT_S1_1_IS_FINAL_CMD_FLAG"
  echo "INFO: S1_2_NEXT_HOST_CMD_ARG=$S1_2_NEXT_HOST_CMD_ARG"
  # ... (outros prints de INFO para as variáveis EXPERIMENT_ e S1_2_ se desejar)


  for req_c in "${REQUEST_COUNTS[@]}"; do
    # Adiciona/Atualiza REQUEST_COUNT e SOURCE_INTERVAL_BETWEEN_REQUESTS no .env
    sed -i '/^REQUEST_COUNT=/d' .env 
    sed -i '/^SOURCE_INTERVAL_BETWEEN_REQUESTS=/d' .env
    echo "REQUEST_COUNT=$req_c" >> .env
    echo "SOURCE_INTERVAL_BETWEEN_REQUESTS=0.5" >> .env # Pode ser ajustado se necessário por experimento

    echo "INFO: EXECUTANDO EXPERIMENTO: Serviços Ativos = $num_active_services, Requisições = $req_c, Perfis = '$PROFILE_ARGS_STRING'"

    # Limpa logs da execução anterior para evitar anexar no volume compartilhado /app/logs
    rm -f "${LOG_DIR_HOST}/source.log" "${LOG_DIR_HOST}/metrics_run.csv"
    rm -f "${METRICS_TEMP_DIR_HOST}/drops_throughput_source.csv" # Se parse_source.py usa este default

    echo "INFO: Iniciando docker-compose up..."
    # Comando docker-compose com perfis
    docker compose -f docker-compose.yml --env-file .env $PROFILE_ARGS_STRING up --build --exit-code-from source --remove-orphans source
    
    exit_code=$?
    echo "INFO: docker-compose up finalizado com código de saída $exit_code."

    # Arquiva resultados
    current_archive_dir="${RESULTS_ARCHIVE_DIR_HOST}/servicos_ativos_${num_active_services}_requisicoes_${req_c}"
    mkdir -p "$current_archive_dir"

    if [ -f "${LOG_DIR_HOST}/source.log" ]; then
      cp "${LOG_DIR_HOST}/source.log" "$current_archive_dir/source.log"
      echo "INFO: source.log copiado para $current_archive_dir"

      echo "INFO: Executando parse_source.py para $current_archive_dir/source.log"
      python parse_source.py \
        --log_file "$current_archive_dir/source.log" \
        --output_csv "$current_archive_dir/drops_throughput_source.csv"
      echo "INFO: parse_source.py finalizado."
    else
      echo "AVISO: ${LOG_DIR_HOST}/source.log não encontrado após a execução."
    fi

    if [ -f "${LOG_DIR_HOST}/metrics_run.csv" ]; then
      cp "${LOG_DIR_HOST}/metrics_run.csv" "$current_archive_dir/metrics_run.csv"
      echo "INFO: metrics_run.csv copiado para $current_archive_dir"
    else
      echo "AVISO: ${LOG_DIR_HOST}/metrics_run.csv não encontrado após a execução."
    fi
    
    echo "INFO: Iniciando docker-compose down..."
    docker compose -f docker-compose.yml --env-file .env $PROFILE_ARGS_STRING down -v 
    echo "INFO: docker-compose down finalizado."
    
    echo "INFO: EXPERIMENTO CONCLUÍDO: Serviços Ativos = $num_active_services, Requisições = $req_c"
    echo "---------------------------------------------------------------------"
    sleep 5 # Breve pausa entre os experimentos
  done
done

# Limpa as variáveis de experimento do .env ao final de tudo
sed -i '/^REQUEST_COUNT=/d' .env
sed -i '/^SOURCE_INTERVAL_BETWEEN_REQUESTS=/d' .env
sed -i '/^EXPERIMENT_LB1_TARGETS=/d' .env
sed -i '/^EXPERIMENT_S1_1_NEXT_HOST_CMD_ARG=/d' .env
sed -i '/^EXPERIMENT_S1_1_NEXT_PORT_CMD_ARG=/d' .env
sed -i '/^EXPERIMENT_S1_1_IS_FINAL_CMD_FLAG=/d' .env
sed -i '/^EXPERIMENT_S1_1_HAS_IA_CMD_FLAG=/d' .env
sed -i '/^S1_2_NEXT_HOST_CMD_ARG=/d' .env
sed -i '/^S1_2_NEXT_PORT_CMD_ARG=/d' .env
sed -i '/^S1_2_IS_FINAL_CMD_FLAG=/d' .env
sed -i '/^S1_2_HAS_IA_CMD_FLAG=/d' .env
sed -i '/^EXPERIMENT_LB2_TARGETS=/d' .env

echo "TODOS OS EXPERIMENTOS FORAM CONCLUÍDOS."