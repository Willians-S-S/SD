# source.py
import time
import threading
import random
import csv
import os
import config # Importa o módulo config
from socket_utils import send_message, start_generic_server

class SourceNode:
    def __init__(self):
        self.name = config.SOURCE_NAME_TAG + (" Docker" if config.IS_DOCKER_ENV else " Local")
        self.prep_time = config.SOURCE_PREP_TIME
        self.compile_time = config.SOURCE_COMPILE_TIME
        self.target_lb1_host = config.SOURCE_TARGET_LB1_HOST
        self.target_lb1_port = config.SOURCE_TARGET_LB1_PORT
        
        self.listen_host = config.HOST_CONFIG['bind_all']
        self.listen_port = config.SOURCE_LISTEN_PORT
        
        self.processed_requests_data = []
        self.results_lock = threading.Lock()
        self.expected_results = config.REQUEST_COUNT
        self.results_received_event = threading.Event()
        
        if config.IS_DOCKER_ENV and not os.path.exists(config.LOGS_DIR_CONTAINER):
            try:
                os.makedirs(config.LOGS_DIR_CONTAINER, exist_ok=True)
                print(f"INFO [{self.name}] Diretório de logs '{config.LOGS_DIR_CONTAINER}' criado/verificado.")
            except OSError as e:
                print(f"ERRO [{self.name}] Falha ao criar diretório de logs '{config.LOGS_DIR_CONTAINER}': {e}")

        print(f"INFO [{self.name}] Inicializando Source. TargetLB1: {self.target_lb1_host}:{self.target_lb1_port}, Listen: {self.listen_host}:{self.listen_port}")
        print(f"INFO [{self.name}] Configuração de Experimento: REQUEST_COUNT={self.expected_results}, INTERVAL_BETWEEN_REQUESTS={config.SOURCE_INTERVAL_BETWEEN_REQUESTS}s, RUN_MODE={config.SOURCE_RUN_MODE}")

    def handle_final_result(self, conn, addr, message_dict):
        with self.results_lock:
            result_payload = message_dict.get('payload', "")
            timestamps = message_dict.get('timestamps', {})
            req_id = timestamps.get('request_id', 'N/A')
            timestamps['M6_source_entry_received_result'] = time.perf_counter()
            print(f"INFO [{self.name}] Req-{req_id}: Resultado FINAL recebido de {addr}: '{str(result_payload)[:100]}...'.")
            self.processed_requests_data.append({'result_payload': result_payload, 'timestamps': timestamps})
            if len(self.processed_requests_data) >= self.expected_results:
                self.results_received_event.set()

    def start_result_listener(self):
        print(f"INFO [{self.name}] Iniciando listener de resultados em {self.listen_host}:{self.listen_port}")
        server_thread = threading.Thread(
            target=start_generic_server,
            args=(self.listen_host, self.listen_port, self.handle_final_result, self.name + "_ResultListener"),
            daemon=True
        )
        server_thread.start()
        return server_thread

    def generate_and_send_requests(self, num_requests):
        print(f"INFO --- [{self.name}] Iniciando Envio de {num_requests} Requisições com Linguagem Natural ---")
        for i in range(num_requests):
            if not self._keep_running_flag.is_set(): 
                print(f"INFO [{self.name}] Envio de requisições interrompido.")
                break
            req_id = i + 1
            text_for_ia = random.choice(config.SAMPLE_IA_TEXTS)
            data_payload = text_for_ia
            timestamps = {'request_id': req_id, 'original_text': text_for_ia}
            timestamps['arrival_interval_setting_s'] = config.SOURCE_INTERVAL_BETWEEN_REQUESTS
            print(f"\nINFO [{self.name}] Req-{req_id}: Preparando frase: '{data_payload[:50]}...' (prep: {self.prep_time:.3f}s).")
            timestamps['M1_source_prep_start'] = time.perf_counter()
            time.sleep(self.prep_time)
            timestamps['M2_source_sent_to_lb1'] = time.perf_counter()
            timestamps[f'{config.LB1_NAME_TAG}_entry'] = timestamps['M2_source_sent_to_lb1']
            print(f"INFO [{self.name}] Req-{req_id}: Enviando para LB1 ({self.target_lb1_host}:{self.target_lb1_port}).")
            message_to_send = {'payload': data_payload, 'timestamps': timestamps}
            if not send_message(self.target_lb1_host, self.target_lb1_port, message_to_send):
                print(f"ERRO FATAL [{self.name}] Req-{req_id}: Falha definitiva ao enviar para LB1.")
            time.sleep(config.SOURCE_INTERVAL_BETWEEN_REQUESTS)
        print(f"INFO [{self.name}] Envio de {num_requests if self._keep_running_flag.is_set() else i} requisições concluído.")


    def compile_and_validate_results(self):
        print(f"\nINFO [{self.name}] Compilando e validando resultados...")
        if not self.processed_requests_data:
            print(f"WARN [{self.name}] Nenhum resultado para compilar.")
            return

        # Ensure LOGS_DIR_CONTAINER exists (it should if running in Docker)
        os.makedirs(config.LOGS_DIR_CONTAINER, exist_ok=True)
        metrics_file_path_container = os.path.join(config.LOGS_DIR_CONTAINER, "metrics_run.csv")
        
        print(f"INFO [{self.name}] Salvando métricas em: {metrics_file_path_container}")
        # In experiment mode, we expect this file to be new each time due to orchestrator cleaning.
        # So, always write header unless file already exists AND is not empty (robustness for non-orchestrated runs).
        write_header = True
        if os.path.exists(metrics_file_path_container) and os.path.getsize(metrics_file_path_container) > 0 :
            # This case should ideally not happen if orchestrator cleans logs/metrics_run.csv
            print(f"WARN [{self.name}] Metrics file {metrics_file_path_container} already exists and is not empty. Appending.")
            write_header = False # If appending, don't write header.

        total_duration_all_requests = 0
        successful_requests_count = 0
        sorted_results = sorted(
            self.processed_requests_data,
            key=lambda x: x["timestamps"].get("request_id", 0),
        )
        with open(metrics_file_path_container, "a", newline="") as csv_fp:
            csv_writer = csv.writer(csv_fp)
            if write_header:
                csv_writer.writerow([
                    "arrival_interval_s", "req_id", "mrt_s",
                    "T1_prep_s", "T2_node02_s", "T3_transit_s1_lb2_s",
                    "T4_node03_s", "T5_transit_s2_source_s",
                    "ia_prediction", "original_text_preview"
                ])
            for item in sorted_results:
                ts = item["timestamps"]
                req_id = ts.get("request_id", "N/A")
                original_text = ts.get("original_text", "N/A")
                final_payload_received = item['result_payload']
                # Try to find IA prediction from any S2 service
                ia_pred_s2 = "N/A_Pred"
                for k_ts in ts:
                    if k_ts.startswith("Service2.") and k_ts.endswith("_ia_prediction"):
                        ia_pred_s2 = ts[k_ts]
                        break
                
                m1, m2, m3 = ts.get('M1_source_prep_start', 0), ts.get('M2_source_sent_to_lb1', 0), ts.get('M3_s1_exit_processed', 0)
                m4, m5, m6 = ts.get(f'{config.LB2_NAME_TAG}_entry_after_transit_S1_LB2', 0), ts.get('M5_s2_exit_processed', 0), ts.get('M6_source_entry_received_result', 0)
                T1, lb1_entry_ts = (m2 - m1) if m1 and m2 else 0, ts.get(f'{config.LB1_NAME_TAG}_entry', m2)
                T2_node02_duration, T3_transit_s1_lb2 = (m3 - lb1_entry_ts) if m3 and lb1_entry_ts else 0, (m4 - m3) if m4 and m3 else 0
                T4_node03_duration, T5_transit_s2_source = (m5 - m4) if m5 and m4 else 0, (m6 - m5) if m6 and m5 else 0
                total_request_time = (m6 - m1) if m6 and m1 else 0
                s1_node_name_found = next((k.split('_entry')[0] for k in ts if k.startswith("Service1.") and k.endswith("_entry")), "S1.X")
                s2_node_name_found = next((k.split('_entry')[0] for k in ts if k.startswith("Service2.") and k.endswith("_entry")), "S2.X")
                print(f"\n--- Tempos para Requisição Req-{req_id} (Texto: '{original_text[:30]}...', Pred: {ia_pred_s2}) ---")
                print(f"    Payload final: {str(final_payload_received)[:100]}...")
                print(f"  T1 (Source Prep): {T1:.4f}s"); print(f"  T2 (Nó 02 - {config.LB1_NAME_TAG} + {s1_node_name_found}): {T2_node02_duration:.4f}s")
                print(f"  T3 (Trânsito S1 -> LB2): {T3_transit_s1_lb2:.4f}s"); print(f"  T4 (Nó 03 - {config.LB2_NAME_TAG} + {s2_node_name_found}): {T4_node03_duration:.4f}s")
                print(f"  T5 (Trânsito S2 -> Source): {T5_transit_s2_source:.4f}s"); print(f"  MRT (M6 - M1): {total_request_time:.4f}s")
                if total_request_time > 0: total_duration_all_requests += total_request_time; successful_requests_count +=1
                csv_writer.writerow([
                    ts.get('arrival_interval_setting_s', config.SOURCE_INTERVAL_BETWEEN_REQUESTS), req_id, f"{total_request_time:.4f}", f"{T1:.4f}",
                    f"{T2_node02_duration:.4f}", f"{T3_transit_s1_lb2:.4f}", f"{T4_node03_duration:.4f}", f"{T5_transit_s2_source:.4f}",
                    ia_pred_s2, original_text[:50].replace('"', '""').replace('\n', ' ')
                ])
        time.sleep(self.compile_time)
        print(f"\nINFO [{self.name}] Compilação final concluída em {self.compile_time:.3f}s.")
        validation_status = "SUCESSO" if len(self.processed_requests_data) >= self.expected_results else f"FALHA ({len(self.processed_requests_data)}/{self.expected_results})"
        print(f"INFO [{self.name}] Status da validação final: {validation_status}.")
        if successful_requests_count > 0:
            avg_duration = total_duration_all_requests / successful_requests_count
            print(f"INFO [{self.name}] Tempo médio total por requisição processada com sucesso: {avg_duration:.4f}s ({successful_requests_count} requests)")
        else: print(f"WARN [{self.name}] Nenhuma requisição processada com sucesso para calcular MRT médio.")
        self.processed_requests_data = []
        self.results_received_event.clear()


    def run_simulation(self):
        self._keep_running_flag = threading.Event() 
        self._keep_running_flag.set() 

        print(f"INFO --- [{self.name}] Iniciando Simulação ({'DOCKER' if config.IS_DOCKER_ENV else 'LOCAL'}) ---")
        print(f"INFO [{self.name}] Usando REQUEST_COUNT={config.REQUEST_COUNT}, INTERVAL_BETWEEN_REQUESTS={config.SOURCE_INTERVAL_BETWEEN_REQUESTS}s")

        listener_thread = self.start_result_listener()
        time.sleep(1.0) 
        if not listener_thread.is_alive() and listener_thread.daemon: time.sleep(0.5)
        if not listener_thread.is_alive():
            print(f"ERRO FATAL [{self.name}] Listener thread não iniciou. Abortando simulação.")
            self._keep_running_flag.clear() 
            return 

        initial_wait_time = 15 if config.IS_DOCKER_ENV else 5 
        print(f"INFO [{self.name}] Aguardando {initial_wait_time}s para os outros nós (LBs, Services) iniciarem e modelos carregarem...")
        time.sleep(initial_wait_time)

        self.generate_and_send_requests(config.REQUEST_COUNT)
        
        print(f"INFO [{self.name}] Todas as requisições ({config.REQUEST_COUNT if self._keep_running_flag.is_set() else 'parciais'}) foram enviadas. Aguardando {self.expected_results} resultados...")
        
        # More generous timeout calculation
        # Base per request: max S1_PROC_TIME + max S2_IA_TIME_ESTIMATE + LBs + transits + source_interval
        # S2_IA_TIME_ESTIMATE: for bert-base, maybe 1-2s per req on CPU. For bert-large, 3-5s or more.
        # Let's estimate IA time generously as 5s for now.
        estimated_processing_per_req = config.SOURCE_INTERVAL_BETWEEN_REQUESTS + 0.2 # S1_times, LB_times, transits
        estimated_ia_time_per_req = 5.0 # Generous estimate for IA processing
        single_req_timeout_est = estimated_processing_per_req + estimated_ia_time_per_req
        
        # For concurrent requests, the total time is not just N * single_req_timeout
        # It's more like (N * interval) + single_req_timeout_for_last_one + buffer
        timeout_seconds = (config.REQUEST_COUNT * config.SOURCE_INTERVAL_BETWEEN_REQUESTS) + single_req_timeout_est + 60 # 60s buffer
        timeout_seconds = max(timeout_seconds, 120.0) # Minimum 120s
        
        print(f"INFO [{self.name}] Timeout para resultados configurado para {timeout_seconds:.1f}s.")

        if self.results_received_event.wait(timeout=timeout_seconds):
            print(f"INFO [{self.name}] Todos os {self.expected_results} resultados foram recebidos.")
        else:
            print(f"WARN [{self.name}] Timeout! ({timeout_seconds:.1f}s). Resultados recebidos: {len(self.processed_requests_data)}/{self.expected_results}.")

        self.compile_and_validate_results()
        print(f"INFO [{self.name}] Ciclo de simulação concluído.")

        if config.SOURCE_RUN_MODE == "interactive":
            print(f"INFO [{self.name}] Simulação principal concluída. Entrando em modo de espera (interactive mode).")
            print(f"INFO [{self.name}] O listener de resultados em {self.listen_host}:{self.listen_port} continua ativo.")
            print(f"INFO [{self.name}] Pressione Ctrl+C para encerrar o Source.")
            try:
                while self._keep_running_flag.is_set(): 
                    time.sleep(10) 
            except KeyboardInterrupt:
                print(f"INFO [{self.name}] KeyboardInterrupt recebido. Encerrando o modo de espera do Source.")
                self._keep_running_flag.clear() 
            finally:
                print(f"INFO [{self.name}] Source encerrando o modo de espera.")
        else: # "experiment" mode or any other value
            print(f"INFO [{self.name}] Simulação principal concluída (experiment mode). Source vai encerrar.")
            self._keep_running_flag.clear() # Ensure any lingering checks will stop
            # Listener thread is daemon, will exit when main thread exits.


if __name__ == "__main__":
    print("INFO [Source Main] Iniciando SourceNode...")
    main_source_node = None
    try:
        main_source_node = SourceNode()
        main_source_node.run_simulation()
    except KeyboardInterrupt:
        print("INFO [Source Main] KeyboardInterrupt global recebido. Tentando encerrar graciosamente...")
        if main_source_node and hasattr(main_source_node, '_keep_running_flag'):
            main_source_node._keep_running_flag.clear() 
    except Exception as e_main_source:
        print(f"ERRO FATAL [Source Main] Erro não tratado na execução do Source: {e_main_source}", exc_info=True)
    finally:
        print(f"INFO [Source Main] Programa Source principal finalizado (RUN_MODE: {config.SOURCE_RUN_MODE}).")