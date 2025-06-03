# service.py
import time
import argparse
import os
import random

import torch # Mova para o topo se usado condicionalmente
from transformers import BertTokenizer # Mova para o topo

from SentimentClassifier import SentimentClassifier
from socket_utils import send_message, start_generic_server
import config

class ServiceNode:
    def __init__(self, name_tag, listen_port, host_to_bind, proc_time_no_ia,
                 next_target_host=None, next_target_port=None,
                 transit_time_to_next=0, is_final_service=False,
                 final_result_target_host=None, final_result_target_port=None,
                 has_ia=False, bert_model_name=None, model_path=None, # model_path é o diretório do .bin
                 num_classes=3, max_len=180, state_dict_filename=None): # state_dict_filename é o nome do .bin
        self.name_tag = name_tag
        self.listen_port = listen_port
        self.host_to_bind = host_to_bind
        self.simulated_proc_time_no_ia = proc_time_no_ia
        self.next_target_host = next_target_host
        self.next_target_port = next_target_port
        self.transit_time_to_next = transit_time_to_next
        self.is_final_service = is_final_service
        self.final_result_target_host = final_result_target_host
        self.final_result_target_port = final_result_target_port

        self.has_ia = has_ia
        self.ai_model = None
        self.tokenizer = None
        self.device = None
        self.max_len = max_len

        print(f"INFO [{self.name_tag}] Inicializando Service. Porta: {self.listen_port}, Host Bind: {self.host_to_bind}, PTimeNoIA: {self.simulated_proc_time_no_ia}, HasIA: {self.has_ia}")

        if self.has_ia:
            print(f"INFO [{self.name_tag}] Configurado com IA. Tentando carregar: BERT='{bert_model_name}', ModelDir='{model_path}', BinFile='{state_dict_filename}'")
            if not bert_model_name:
                print(f"ERRO CRÍTICO [{self.name_tag}] Para has_ia=True, bert_model_name é obrigatório.")
                self.has_ia = False
            else:
                try:
                    self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
                    print(f"INFO [{self.name_tag}] Usando dispositivo: {self.device}")

                    print(f"INFO [{self.name_tag}] Carregando Tokenizer: '{bert_model_name}'")
                    self.tokenizer = BertTokenizer.from_pretrained(bert_model_name)

                    print(f"INFO [{self.name_tag}] Instanciando SentimentClassifier com base: '{bert_model_name}', Classes: {num_classes}")
                    self.ai_model = SentimentClassifier(num_classes, pre_trained_model_path_or_name=bert_model_name)
                    self.ai_model = self.ai_model.to(self.device)

                    if state_dict_filename and state_dict_filename.strip() and model_path and model_path.strip():
                        print(f"INFO [{self.name_tag}] Tentando carregar state_dict: '{state_dict_filename}' de '{model_path}'")
                        
                        # Caminho absoluto para o arquivo .bin dentro do container
                        # model_path já deve ser o caminho DENTRO do container (ex: /app/bert_model_data)
                        path_opt1 = os.path.join(model_path, 'models', state_dict_filename) # Se estiver em subpasta 'models'
                        path_opt2 = os.path.join(model_path, state_dict_filename) # Se estiver direto na pasta
                        actual_state_dict_path = None

                        if os.path.exists(path_opt1): actual_state_dict_path = path_opt1
                        elif os.path.exists(path_opt2): actual_state_dict_path = path_opt2
                        
                        if actual_state_dict_path:
                            print(f"INFO [{self.name_tag}] Carregando state_dict fine-tuned de: {actual_state_dict_path}")
                            self.ai_model.load_state_dict(torch.load(actual_state_dict_path, map_location=self.device))
                            print(f"INFO [{self.name_tag}] State_dict '{state_dict_filename}' carregado com sucesso.")
                        else:
                            print(f"AVISO [{self.name_tag}] Arquivo state_dict '{state_dict_filename}' NÃO encontrado em '{model_path}' (Opções: {path_opt1}, {path_opt2}). Usando modelo base sem pesos fine-tuned.")
                    elif state_dict_filename and state_dict_filename.strip():
                         print(f"AVISO [{self.name_tag}] 'state_dict_filename' ('{state_dict_filename}') fornecido, mas 'model_path' está vazio ou não foi fornecido. Não é possível carregar .bin. Usando modelo base.")
                    else:
                        print(f"AVISO [{self.name_tag}] Nenhum 'state_dict_filename' válido fornecido. Usando modelo base BERT ({bert_model_name}) sem pesos fine-tuned específicos.")
                    
                    self.ai_model.eval()
                    print(f"INFO [{self.name_tag}] Modelo de IA (base: {bert_model_name}) e Tokenizer carregados e prontos.")
                except Exception as e:
                    print(f"ERRO CRÍTICO [{self.name_tag}] Ao carregar modelo/tokenizer: {e}", exc_info=True)
                    self.has_ia = False # Desabilita IA se falhar
                    self.ai_model = None
                    self.tokenizer = None
        else:
            print(f"INFO [{self.name_tag}] Configurado SEM IA. Atuará como encaminhador/simulador de tempo.")


    def _perform_ia_processing(self, text_to_process):
        if not self.has_ia or not self.ai_model or not self.tokenizer:
            delay_ms = self.simulated_proc_time_no_ia * 1000
            if delay_ms <= 0: delay_ms = random.uniform(10, 50)
            time.sleep(delay_ms / 1000.0)
            print(f"DEBUG [{self.name_tag}] (Sem IA ativa/falha) Simulado delay de {delay_ms:.3f} ms.")
            return "-NO_IA_OR_FAIL-", delay_ms

        print(f"DEBUG [{self.name_tag}] Iniciando processamento IA para: '{text_to_process[:50]}...'")
        start_time_ia = time.perf_counter()
        prediction_output = "-ERR_IA-"
        try:
            encoding = self.tokenizer.encode_plus(
                text_to_process, add_special_tokens=True, max_length=self.max_len,
                return_token_type_ids=False, padding='max_length',
                truncation=True, return_attention_mask=True, return_tensors='pt')
            input_ids = encoding['input_ids'].to(self.device)
            attention_mask = encoding['attention_mask'].to(self.device)
            with torch.no_grad():
                outputs = self.ai_model(input_ids, attention_mask)
                _, preds_tensor = torch.max(outputs, dim=1)
                prediction_output = str(preds_tensor.item())
        except Exception as e:
            print(f"ERRO [{self.name_tag}] Na predição da IA: {e}", exc_info=True)

        processing_time_ms = (time.perf_counter() - start_time_ia) * 1000.0
        print(f"INFO [{self.name_tag}] IA concluída. Duração: {processing_time_ms:.3f} ms. Predição: {prediction_output}")
        return prediction_output, processing_time_ms

    def handle_request(self, conn, addr, message_dict):
        original_data = message_dict.get('payload', "")
        timestamps = message_dict.get('timestamps', {})
        req_id = timestamps.get('request_id', 'N/A')

        timestamps[f'{self.name_tag}_entry'] = time.perf_counter()
        print(f"INFO [{self.name_tag}] Req-{req_id}: Recebeu de {addr}, dados: '{str(original_data)[:60]}...'.")

        processed_data_payload = original_data
        ia_prediction_result = None

        if self.has_ia:
            ia_prediction_result, _ = self._perform_ia_processing(str(original_data))
            processed_data_payload = f"{original_data} [IA_Pred:{ia_prediction_result}]"
        else:
            time.sleep(self.simulated_proc_time_no_ia)
            processed_data_payload = f"{original_data} (processado por {self.name_tag} - SEM IA)"

        timestamps[f'{self.name_tag}_exit_processed'] = time.perf_counter()
        duration = timestamps[f'{self.name_tag}_exit_processed'] - timestamps[f'{self.name_tag}_entry']
        print(f"INFO [{self.name_tag}] Req-{req_id}: Processou (Tempo real: {duration:.4f}s). Payload final: '{str(processed_data_payload)[:60]}...'.")

        if self.name_tag.startswith("Service1"):
            timestamps['M3_s1_exit_processed'] = timestamps[f'{self.name_tag}_exit_processed']
        elif self.name_tag.startswith("Service2"):
            timestamps['M5_s2_exit_processed'] = timestamps[f'{self.name_tag}_exit_processed']
            if ia_prediction_result is not None:
                 timestamps[f'{self.name_tag}_ia_prediction'] = ia_prediction_result

        next_message = {'payload': processed_data_payload, 'timestamps': timestamps}

        if self.transit_time_to_next > 0:
            print(f"DEBUG [{self.name_tag}] Req-{req_id}: Simulando trânsito ({self.transit_time_to_next:.2f}s)...")
            time.sleep(self.transit_time_to_next)

        if self.is_final_service:
            if self.final_result_target_host and self.final_result_target_port:
                print(f"INFO [{self.name_tag}] Req-{req_id}: Enviando resultado final para Source em {self.final_result_target_host}:{self.final_result_target_port}.")
                if not send_message(self.final_result_target_host, int(self.final_result_target_port), next_message):
                    print(f"ERRO [{self.name_tag}] Req-{req_id}: Falha ao enviar resultado final para Source.")
            else:
                print(f"ERRO [{self.name_tag}] Req-{req_id}: Serviço final mas sem alvo para resultado final.")
        elif self.next_target_host and self.next_target_port:
            if self.name_tag.startswith("Service1"):
                timestamps[f'{config.LB2_NAME_TAG}_entry_after_transit_S1_LB2'] = time.perf_counter()
            print(f"INFO [{self.name_tag}] Req-{req_id}: Encaminhando para {self.next_target_host}:{self.next_target_port}.")
            if not send_message(self.next_target_host, int(self.next_target_port), next_message):
                 print(f"ERRO [{self.name_tag}] Req-{req_id}: Falha ao encaminhar para {self.next_target_host}:{self.next_target_port}.")
        else:
            print(f"INFO [{self.name_tag}] Req-{req_id}: Processamento concluído, sem próximo alvo configurado.")

    def start(self):
        print(f"INFO [{self.name_tag}] Chamando start_generic_server para {self.host_to_bind}:{self.listen_port}")
        start_generic_server(self.host_to_bind, self.listen_port, self.handle_request, self.name_tag)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Service Node")
    parser.add_argument("--name", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--host", default=config.HOST_CONFIG['bind_all'])
    parser.add_argument("--ptime_no_ia", type=float, required=True, help="Tempo de processamento simulado (se sem IA ou IA falhar)")
    parser.add_argument("--next_host")
    parser.add_argument("--next_port", type=int)
    parser.add_argument("--transit_time", type=float, default=0)
    parser.add_argument("--is_final", action="store_true")
    parser.add_argument("--final_target_host")
    parser.add_argument("--final_target_port", type=int)
    # IA args
    parser.add_argument("--has_ia", action="store_true")
    parser.add_argument("--bert_model_name", default=config.S2_DEFAULT_BERT_MODEL_NAME)
    parser.add_argument("--model_path", default=(config.S2_DEFAULT_MODEL_PATH_DOCKER if config.IS_DOCKER_ENV else config.S2_DEFAULT_MODEL_PATH_LOCAL))
    parser.add_argument("--num_classes", type=int, default=config.S2_DEFAULT_NUM_CLASSES)
    parser.add_argument("--max_len", type=int, default=config.S2_DEFAULT_MAX_LEN)
    parser.add_argument("--state_dict_filename", default=config.S2_DEFAULT_STATE_DICT_FILENAME)

    args = parser.parse_args()
    print(f"INFO [Service Main] Argumentos recebidos: {args}")

    # Determinar o model_path correto com base no ambiente, mesmo que o default já tente fazer isso.
    # O argumento --model_path no docker-compose já deve passar o CAMINHO_MODELO_BERT_CONTAINER
    effective_model_path = args.model_path
    if args.has_ia and config.IS_DOCKER_ENV:
        effective_model_path = config.CAMINHO_MODELO_BERT_CONTAINER # Garante o caminho do container
    elif args.has_ia and not config.IS_DOCKER_ENV:
        effective_model_path = config.CAMINHO_MODELO_BERT_HOST_PY # Garante o caminho do host para local

    print(f"INFO [Service Main] Configurando ServiceNode: name='{args.name}', port={args.port}, host_bind='{args.host}', ptime_no_ia={args.ptime_no_ia}, has_ia={args.has_ia}")
    if args.has_ia:
        print(f"INFO [Service Main] IA Config: BERT='{args.bert_model_name}', ModelDir='{effective_model_path}', BinFile='{args.state_dict_filename}'")

    try:
        service = ServiceNode(
            name_tag=args.name,
            listen_port=args.port,
            host_to_bind=args.host,
            proc_time_no_ia=args.ptime_no_ia,
            next_target_host=args.next_host,
            next_target_port=args.next_port,
            transit_time_to_next=args.transit_time,
            is_final_service=args.is_final,
            final_result_target_host=args.final_target_host,
            final_result_target_port=args.final_target_port,
            has_ia=args.has_ia,
            bert_model_name=args.bert_model_name,
            model_path=effective_model_path, # Usar o caminho efetivo
            num_classes=args.num_classes,
            max_len=args.max_len,
            state_dict_filename=args.state_dict_filename
        )
        service.start()
    except Exception as e_init:
        print(f"ERRO FATAL [Service Main] Ao instanciar ou iniciar ServiceNode: {e_init}", exc_info=True)
        exit(1)