# service.py
import time
import argparse
from socket_utils import send_message, start_generic_server
# Configurações serão passadas via argparse ou importadas de config.py se não usar argparse

class ServiceNode:
    def __init__(self, name_tag, listen_port, host, proc_time, 
                 next_target_host=None, next_target_port=None, 
                 transit_time_to_next=0, is_final_service=False,
                 final_result_target_host=None, final_result_target_port=None):
        self.name_tag = name_tag
        self.listen_port = listen_port
        self.host = host
        self.processing_time = proc_time
        self.next_target_host = next_target_host
        self.next_target_port = next_target_port
        self.transit_time_to_next = transit_time_to_next
        self.is_final_service = is_final_service
        # Usado apenas se is_final_service for True
        self.final_result_target_host = final_result_target_host 
        self.final_result_target_port = final_result_target_port


    def handle_request(self, conn, addr, message_dict):
        data = message_dict['payload']
        timestamps = message_dict['timestamps']
        req_id = timestamps.get('request_id', 'N/A')

        timestamps[f'{self.name_tag}_entry'] = time.perf_counter()
        print(f"[{self.name_tag}] Req-{req_id}: Recebeu de {addr}, dados: '{data}'. Proc: {self.processing_time:.2f}s.")
        
        time.sleep(self.processing_time)
        
        processed_data = f"{data} (processado por {self.name_tag})"
        timestamps[f'{self.name_tag}_exit_processed'] = time.perf_counter()
        duration = timestamps[f'{self.name_tag}_exit_processed'] - timestamps[f'{self.name_tag}_entry']
        print(f"[{self.name_tag}] Req-{req_id}: Processou '{data}' em {duration:.4f}s. Resultado: '{processed_data}'.")

        # Mapeamento dos pontos M
        if self.name_tag.startswith("Service1"): # S1.X
            timestamps['M3_s1_exit_processed'] = timestamps[f'{self.name_tag}_exit_processed']
        elif self.name_tag.startswith("Service2"): # S2.X
            timestamps['M5_s2_exit_processed'] = timestamps[f'{self.name_tag}_exit_processed']

        # Preparar mensagem para o próximo
        next_message = {'payload': processed_data, 'timestamps': timestamps}

        if self.transit_time_to_next > 0:
            print(f"[{self.name_tag}] Req-{req_id}: Simulando trânsito ({self.transit_time_to_next:.2f}s)...")
            time.sleep(self.transit_time_to_next)
        
        if self.is_final_service:
            if self.final_result_target_host and self.final_result_target_port:
                timestamps['M6_source_entry_received_result'] = time.perf_counter() # Ponto de chegada no Source
                print(f"[{self.name_tag}] Req-{req_id}: Enviando resultado final para Source em {self.final_result_target_host}:{self.final_result_target_port}.")
                send_message(self.final_result_target_host, self.final_result_target_port, next_message)
            else:
                print(f"[{self.name_tag}] Req-{req_id}: ERRO - Serviço final mas sem alvo para resultado final.")
        elif self.next_target_host and self.next_target_port:
            # Ponto de chegada no próximo componente (ex: LB2)
            if self.name_tag.startswith("Service1"): # Saindo de S1 para LB2
                timestamps[f'{config.LB2_NAME_TAG}_entry_after_transit_S1_LB2'] = time.perf_counter() 
            
            print(f"[{self.name_tag}] Req-{req_id}: Encaminhando para {self.next_target_host}:{self.next_target_port}.")
            send_message(self.next_target_host, self.next_target_port, next_message)
        else:
            print(f"[{self.name_tag}] Req-{req_id}: Processamento concluído, sem próximo alvo configurado.")
            
    def start(self):
        start_generic_server(self.host, self.listen_port, self.handle_request, self.name_tag)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Service Node")
    parser.add_argument("--name", required=True, help="Nome/Tag do serviço (ex: Service1.1_Nó02)")
    parser.add_argument("--port", type=int, required=True, help="Porta de escuta")
    parser.add_argument("--host", default="127.0.0.1", help="Host de escuta")
    parser.add_argument("--ptime", type=float, required=True, help="Tempo de processamento")
    parser.add_argument("--next_host", help="Host do próximo alvo")
    parser.add_argument("--next_port", type=int, help="Porta do próximo alvo")
    parser.add_argument("--transit_time", type=float, default=0, help="Tempo de trânsito para o próximo alvo")
    parser.add_argument("--is_final", action="store_true", help="Se este é um serviço final")
    parser.add_argument("--final_target_host", help="Host do Source (se is_final)")
    parser.add_argument("--final_target_port", type=int, help="Porta do Source (se is_final)")
    
    args = parser.parse_args()

    # Para que o config seja importado no contexto do if __name__ == "__main__":
    import config 

    service = ServiceNode(
        name_tag=args.name,
        listen_port=args.port,
        host=args.host,
        proc_time=args.ptime,
        next_target_host=args.next_host,
        next_target_port=args.next_port,
        transit_time_to_next=args.transit_time,
        is_final_service=args.is_final,
        final_result_target_host=args.final_target_host,
        final_result_target_port=args.final_target_port
    )
    service.start()