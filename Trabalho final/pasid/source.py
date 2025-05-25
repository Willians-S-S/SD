# source.py
import time
import threading
import config # Importa todas as configurações
from socket_utils import send_message, start_generic_server
import subprocess # Módulo para rodar subprocessos
import sys # Para obter o caminho do interpretador Python atual
import os # Para construir caminhos de script de forma mais robusta

class SourceNode:
    def __init__(self):
        self.name = "Source (Nó 01)"
        self.prep_time = config.SOURCE_PREP_TIME
        self.compile_time = config.SOURCE_COMPILE_TIME
        self.target_lb1_host = config.SOURCE_TARGET_LB1_HOST
        self.target_lb1_port = config.SOURCE_TARGET_LB1_PORT
        
        self.listen_host = config.HOST
        self.listen_port = config.SOURCE_LISTEN_PORT
        
        self.processed_requests_data = []
        self.results_lock = threading.Lock()
        self.expected_results = config.REQUEST_COUNT
        self.results_received_event = threading.Event()
        
        self.subprocesses = [] # Lista para manter referência aos subprocessos iniciados

    def _get_script_path(self, script_name):
        # Assume que os scripts estão no mesmo diretório que source.py
        base_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_dir, script_name)

    def _launch_node(self, script_name, args):
        """Lança um nó como um subprocesso."""
        script_path = self._get_script_path(script_name)
        command = [sys.executable, script_path] + args
        try:
            # Inicia o processo. stdout e stderr podem ser capturados se necessário.
            # Para este exemplo, eles irão para o console do Source.
            process = subprocess.Popen(command)
            self.subprocesses.append(process)
            print(f"INFO [{self.name} Orchestrator]: Iniciado {script_name} com PID {process.pid} (Args: {' '.join(args)})")
            return process
        except FileNotFoundError:
            print(f"ERRO [{self.name} Orchestrator]: Script '{script_path}' não encontrado.")
        except Exception as e:
            print(f"ERRO [{self.name} Orchestrator]: Falha ao iniciar {script_name} (Args: {' '.join(args)}): {e}")
        return None

    def _launch_all_dependent_nodes(self): 
        """Inicia todos os nós de serviço e load balancer."""
        print(f"--- [{self.name} Orchestrator]: Iniciando nós dependentes ---")
        
        # A ordem de inicialização é importante:
        # 1. Serviços finais (S2.x)
        # 2. Load Balancer que os serve (LB2)
        # 3. Serviços intermediários (S1.x)
        # 4. Load Balancer que os serve (LB1)

        # Serviços S2.x
        self._launch_node("service.py", [
            "--name", config.S2_1_NAME_TAG, "--port", str(config.S2_1_LISTEN_PORT),
            "--ptime", str(config.S2_1_PROC_TIME), "--is_final",
            "--final_target_host", config.S2_1_NEXT_TARGET_HOST, "--final_target_port", str(config.S2_1_NEXT_TARGET_PORT),
            # CORREÇÃO APLICADA:
            "--transit_time", str(config.S2_1_TRANSIT_TIME_TO_NEXT)
        ])
        self._launch_node("service.py", [
            "--name", config.S2_2_NAME_TAG, "--port", str(config.S2_2_LISTEN_PORT),
            "--ptime", str(config.S2_2_PROC_TIME), "--is_final",
            "--final_target_host", config.S2_2_NEXT_TARGET_HOST, "--final_target_port", str(config.S2_2_NEXT_TARGET_PORT),
            # CORREÇÃO APLICADA:
            "--transit_time", str(config.S2_2_TRANSIT_TIME_TO_NEXT)
        ])
        time.sleep(1.5) # Pausa para os serviços S2 iniciarem

        # LoadBalancer LB2
        lb2_targets = f"{config.HOST}:{config.S2_1_LISTEN_PORT},{config.HOST}:{config.S2_2_LISTEN_PORT}"
        self._launch_node("loadbalancer.py", [
            "--name", config.LB2_NAME_TAG, "--port", str(config.LB2_LISTEN_PORT),
            "--ptime", str(config.LB2_PROC_TIME), "--targets", lb2_targets
        ])
        time.sleep(1.5) # Pausa para LB2 iniciar

        # Serviços S1.x
        self._launch_node("service.py", [
            "--name", config.S1_1_NAME_TAG, "--port", str(config.S1_1_LISTEN_PORT),
            "--ptime", str(config.S1_1_PROC_TIME),
            "--next_host", config.S1_1_NEXT_TARGET_HOST, "--next_port", str(config.S1_1_NEXT_TARGET_PORT),
            # CORREÇÃO APLICADA:
            "--transit_time", str(config.S1_1_TRANSIT_TIME_TO_NEXT)
        ])
        self._launch_node("service.py", [
            "--name", config.S1_2_NAME_TAG, "--port", str(config.S1_2_LISTEN_PORT),
            "--ptime", str(config.S1_2_PROC_TIME),
            "--next_host", config.S1_2_NEXT_TARGET_HOST, "--next_port", str(config.S1_2_NEXT_TARGET_PORT),
            # CORREÇÃO APLICADA:
            "--transit_time", str(config.S1_2_TRANSIT_TIME_TO_NEXT)
        ])
        time.sleep(1.5) # Pausa para os serviços S1 iniciarem

        # LoadBalancer LB1
        lb1_targets = f"{config.HOST}:{config.S1_1_LISTEN_PORT},{config.HOST}:{config.S1_2_LISTEN_PORT}"
        self._launch_node("loadbalancer.py", [
            "--name", config.LB1_NAME_TAG, "--port", str(config.LB1_LISTEN_PORT),
            "--ptime", str(config.LB1_PROC_TIME), "--targets", lb1_targets
        ])
        time.sleep(1.5) # Pausa para LB1 iniciar

        print(f"--- [{self.name} Orchestrator]: Todos os nós dependentes foram solicitados para iniciar. ---")

    def _terminate_all_dependent_nodes(self):
        """Tenta encerrar todos os subprocessos iniciados."""
        print(f"--- [{self.name} Orchestrator]: Encerrando nós dependentes ---")
        for i, process in enumerate(self.subprocesses):
            if process.poll() is None:  # Verifica se o processo ainda está rodando
                print(f"Encerrando subprocesso {i+1} (PID {process.pid})...")
                try:
                    process.terminate()  # Envia SIGTERM (tentativa de encerramento gracioso)
                    process.wait(timeout=5)  # Espera até 5 segundos para o processo encerrar
                except subprocess.TimeoutExpired:
                    print(f"Subprocesso PID {process.pid} não encerrou graciosamente. Forçando (kill)...")
                    process.kill()  # Envia SIGKILL (força o encerramento)
                except Exception as e:
                    print(f"Erro ao tentar encerrar subprocesso PID {process.pid}: {e}")
            else:
                print(f"Subprocesso {i+1} (PID {process.pid}) já havia encerrado com código {process.poll()}.")
        self.subprocesses = []


    def handle_final_result(self, conn, addr, message_dict):
        with self.results_lock:
            result = message_dict['payload']
            timestamps = message_dict['timestamps']
            req_id = timestamps.get('request_id', 'N/A')
            print(f"[{self.name}] Req-{req_id}: Resultado FINAL recebido de {addr}: '{result}'.")
            self.processed_requests_data.append({'result': result, 'timestamps': timestamps})
            
            if len(self.processed_requests_data) >= self.expected_results:
                self.results_received_event.set()

    def start_result_listener(self):
        print(f"[{self.name}] Iniciando listener de resultados em {self.listen_host}:{self.listen_port}")
        server_thread = threading.Thread(
            target=start_generic_server, 
            args=(self.listen_host, self.listen_port, self.handle_final_result, self.name + "_ResultListener"),
            daemon=True
        )
        server_thread.start()
        return server_thread

    def generate_and_send_requests(self, num_requests):
        print(f"--- [{self.name}] Iniciando Envio de {num_requests} Requisições ---")
        for i in range(num_requests):
            req_id = i + 1
            data_payload = f"Pacote_Dados_Req_{req_id}"
            timestamps = {'request_id': req_id}

            print(f"\n[{self.name}] Req-{req_id}: Preparando '{data_payload}' (prep: {self.prep_time:.2f}s).")
            timestamps['M1_source_prep_start'] = time.perf_counter()
            time.sleep(self.prep_time)
            
            timestamps['M2_source_sent_to_lb1'] = time.perf_counter()
            timestamps[f'{config.LB1_NAME_TAG}_entry'] = timestamps['M2_source_sent_to_lb1']

            print(f"[{self.name}] Req-{req_id}: Enviando para LB1 ({self.target_lb1_host}:{self.target_lb1_port}).")
            message_to_send = {'payload': data_payload, 'timestamps': timestamps}
            send_message(self.target_lb1_host, self.target_lb1_port, message_to_send)
            time.sleep(0.2) # Pausa entre envios

    def compile_and_validate_results(self):
        print(f"\n[{self.name}] Compilando e validando resultados...")
        if not self.processed_requests_data:
            print(f"[{self.name}] Nenhum resultado para compilar.")
            return

        total_duration_all_requests = 0
        # Ordenar por request_id para melhor visualização
        sorted_results = sorted(self.processed_requests_data, key=lambda x: x['timestamps'].get('request_id', 0))

        for item in sorted_results:
            ts = item['timestamps']
            req_id = ts.get('request_id', 'N/A')
            print(f"\n--- Tempos para Requisição Req-{req_id} ---")

            T1 = ts.get('M2_source_sent_to_lb1', 0) - ts.get('M1_source_prep_start', 0)
            print(f"  T1 (Source Prep): {T1:.4f}s (M2 - M1)")

            # Nó 02 (LB1 + S1.X)
            lb1_entry = ts.get(f'{config.LB1_NAME_TAG}_entry', ts.get('M2_source_sent_to_lb1',0))
            lb1_exit = ts.get(f'{config.LB1_NAME_TAG}_exit_distributed',0)
            
            s1_name_found = next((k.split('_entry')[0] for k in ts if k.startswith("Service1") and k.endswith("_entry")), None)
            s1_entry = ts.get(f'{s1_name_found}_entry',0) if s1_name_found else 0
            m3_s1_exit = ts.get('M3_s1_exit_processed',0)

            T2_lb1_duration = lb1_exit - lb1_entry if lb1_exit and lb1_entry else 0
            T2_s1_duration = m3_s1_exit - s1_entry if m3_s1_exit and s1_entry else 0
            T2 = T2_lb1_duration + T2_s1_duration
            if s1_name_found:
                 print(f"    Tempo em {config.LB1_NAME_TAG}: {T2_lb1_duration:.4f}s")
                 print(f"    Tempo em {s1_name_found}: {T2_s1_duration:.4f}s")
            print(f"  T2 (Nó 02 - {config.LB1_NAME_TAG} + {s1_name_found or 'S1.X'}): {T2:.4f}s (M3 - M2)")

            # T3: Trânsito S1 -> LB2
            m4_lb2_entry = ts.get(f'{config.LB2_NAME_TAG}_entry_after_transit_S1_LB2',0)
            T3 = m4_lb2_entry - m3_s1_exit if m4_lb2_entry and m3_s1_exit else 0
            print(f"  T3 (Trânsito S1 -> LB2): {T3:.4f}s (M4 - M3)")

            # Nó 03 (LB2 + S2.X)
            lb2_exit = ts.get(f'{config.LB2_NAME_TAG}_exit_distributed',0)
            s2_name_found = next((k.split('_entry')[0] for k in ts if k.startswith("Service2") and k.endswith("_entry")), None)
            s2_entry = ts.get(f'{s2_name_found}_entry',0) if s2_name_found else 0
            m5_s2_exit = ts.get('M5_s2_exit_processed',0)
            
            T4_lb2_duration = lb2_exit - m4_lb2_entry if lb2_exit and m4_lb2_entry else 0
            T4_s2_duration = m5_s2_exit - s2_entry if m5_s2_exit and s2_entry else 0
            T4 = T4_lb2_duration + T4_s2_duration
            if s2_name_found:
                print(f"    Tempo em {config.LB2_NAME_TAG}: {T4_lb2_duration:.4f}s")
                print(f"    Tempo em {s2_name_found}: {T4_s2_duration:.4f}s")
            print(f"  T4 (Nó 03 - {config.LB2_NAME_TAG} + {s2_name_found or 'S2.X'}): {T4:.4f}s (M5 - M4)")

            # T5: Trânsito S2 -> Source
            m6_source_entry = ts.get('M6_source_entry_received_result',0)
            T5 = m6_source_entry - m5_s2_exit if m6_source_entry and m5_s2_exit else 0
            print(f"  T5 (Trânsito S2 -> Source): {T5:.4f}s (M6 - M5)")
            
            total_request_time = m6_source_entry - ts.get('M1_source_prep_start',0) if m6_source_entry and ts.get('M1_source_prep_start') else 0
            print(f"  Tempo Total da Requisição (M6 - M1): {total_request_time:.4f}s")
            if total_request_time > 0 : total_duration_all_requests += total_request_time
            
            sum_Ts = T1 + T2 + T3 + T4 + T5
            print(f"  Soma (T1+T2+T3+T4+T5): {sum_Ts:.4f}s")

        time.sleep(self.compile_time)
        print(f"\n[{self.name}] Compilação final concluída em {self.compile_time:.2f}s.")
        validation_status = "SUCESSO" if len(self.processed_requests_data) >= self.expected_results else "FALHA (resultados incompletos)"
        print(f"[{self.name}] Status da validação final: {validation_status}.")
        print(f"[{self.name}] Total de resultados compilados: {len(self.processed_requests_data)} de {self.expected_results} esperados.")
        if total_duration_all_requests > 0 and len(self.processed_requests_data) > 0:
            avg_duration = total_duration_all_requests / len(self.processed_requests_data)
            print(f"[{self.name}] Tempo médio total por requisição processada: {avg_duration:.4f}s")


    def run_simulation(self):
        # Envolve o lançamento e encerramento dos nós em um bloco try/finally
        try:
            self._launch_all_dependent_nodes()
            
            # Pausa crucial para garantir que todos os servidores estejam escutando
            print(f"--- [{self.name} Orchestrator]: Aguardando inicialização dos nós (aprox. 5s)... ---")
            time.sleep(5.0) # Ajuste este tempo conforme necessário

            listener_thread = self.start_result_listener()
            time.sleep(1.0) # Pausa para o listener do Source iniciar

            self.generate_and_send_requests(config.REQUEST_COUNT)
            
            print(f"[{self.name}] Todas as requisições foram enviadas. Aguardando {self.expected_results} resultados...")
            
            timeout_seconds = 30 
            if self.results_received_event.wait(timeout=timeout_seconds):
                print(f"[{self.name}] Todos os {self.expected_results} resultados foram recebidos.")
            else:
                print(f"[{self.name}] Timeout! Nem todos os resultados foram recebidos em {timeout_seconds}s. Compilando com {len(self.processed_requests_data)} resultados.")

            self.compile_and_validate_results()

        except Exception as e:
            print(f"ERRO GERAL NA SIMULAÇÃO DO SOURCE: {e}")
        finally:
            self._terminate_all_dependent_nodes()
            print(f"[{self.name}] Simulação concluída.")

if __name__ == "__main__":
    source = SourceNode()
    source.run_simulation()