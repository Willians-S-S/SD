# loadbalancer.py
import time
import argparse
from socket_utils import send_message, start_generic_server
import config

class LoadBalancerNode:
    def __init__(self, name_tag, listen_port, host_to_bind, proc_time, target_hosts, target_ports):
        self.name_tag = name_tag
        self.listen_port = listen_port
        self.host_to_bind = host_to_bind
        self.processing_time = proc_time
        self.target_hosts = target_hosts
        self.target_ports = target_ports
        self.current_target_index = 0

        print(f"INFO [{self.name_tag}] Inicializando LB. Porta: {self.listen_port}, Host Bind: {self.host_to_bind}, PTime: {self.processing_time}")
        if not target_hosts or not target_ports or len(target_hosts) != len(target_ports):
            print(f"ERRO FATAL [{self.name_tag}] Configuração de alvos inválida. Hosts: {target_hosts}, Portas: {target_ports}")
            raise ValueError("Hosts e Portas alvo do LoadBalancer mal configurados ou vazios.")
        print(f"INFO [{self.name_tag}] Alvos configurados: Hosts={target_hosts}, Portas={target_ports}")


    def handle_request(self, conn, addr, message_dict):
        data = message_dict.get('payload', "")
        timestamps = message_dict.get('timestamps', {})
        req_id = timestamps.get('request_id', 'N/A')

        entry_ts_key = None
        current_time = time.perf_counter()

        if self.name_tag == config.LB1_NAME_TAG:
            entry_ts_key = f'{config.LB1_NAME_TAG}_entry'
            if entry_ts_key not in timestamps:
                 timestamps[entry_ts_key] = timestamps.get('M2_source_sent_to_lb1', current_time)
        elif self.name_tag == config.LB2_NAME_TAG:
            entry_ts_key = f'{config.LB2_NAME_TAG}_entry_after_transit_S1_LB2'
            if entry_ts_key not in timestamps:
                timestamps[entry_ts_key] = current_time
        else:
            entry_ts_key = f'{self.name_tag}_entry_fallback'
            timestamps[entry_ts_key] = current_time
        
        entry_timestamp_value = timestamps[entry_ts_key]

        print(f"INFO [{self.name_tag}] Req-{req_id}: Recebeu de {addr}, dados: '{str(data)[:60]}...'. Tempo sim. LB: {self.processing_time:.3f}s.")
        
        time.sleep(self.processing_time)

        selected_host = self.target_hosts[self.current_target_index]
        selected_port = self.target_ports[self.current_target_index]
        self.current_target_index = (self.current_target_index + 1) % len(self.target_ports)
        
        timestamps[f'{self.name_tag}_exit_distributed'] = time.perf_counter()
        duration_in_lb = timestamps[f'{self.name_tag}_exit_distributed'] - entry_timestamp_value
        
        print(f"INFO [{self.name_tag}] Req-{req_id}: Distribuição em {duration_in_lb:.4f}s. Enviando para {selected_host}:{selected_port}.")

        next_message = {'payload': data, 'timestamps': timestamps}
        
        if not send_message(selected_host, int(selected_port), next_message):
            # ➡️ Marca descarte para estatística
            print(f"[DROP] Req={req_id} host={selected_host}:{selected_port} from_lb={self.name_tag}") # Adicionado from_lb
            print(f"ERRO [{self.name_tag}] Req-{req_id}: Falha ao enviar mensagem para {selected_host}:{selected_port}.")


    def start(self):
        print(f"INFO [{self.name_tag}] Chamando start_generic_server para {self.host_to_bind}:{self.listen_port}")
        start_generic_server(self.host_to_bind, self.listen_port, self.handle_request, self.name_tag)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Balancer Node")
    parser.add_argument("--name", required=True, help="Nome/Tag do LB (ex: LoadBalancer1_Nó02)")
    parser.add_argument("--port", type=int, required=True, help="Porta de escuta")
    parser.add_argument("--host", default=config.HOST_CONFIG['bind_all'], help="Host de escuta (padrão 0.0.0.0 para Docker)")
    parser.add_argument("--ptime", type=float, required=True, help="Tempo de processamento/distribuição do LB")
    parser.add_argument("--targets", required=True, help="Lista de alvos no formato host1:port1,host2:port2,...")
    
    args = parser.parse_args()
    print(f"INFO [LB Main] Argumentos recebidos: {args}")

    target_hosts_list = []
    target_ports_list = []
    try:
        if args.targets:
            for target_str in args.targets.split(','):
                host_val, port_str_val = target_str.strip().split(':')
                target_hosts_list.append(host_val)
                target_ports_list.append(int(port_str_val))
        if not target_hosts_list:
             print("ERRO FATAL [LB Main] Lista de alvos está vazia após o parse.")
             exit(1)
    except ValueError as e:
        print(f"ERRO FATAL [LB Main] Formato de --targets ('{args.targets}') inválido: {e}. Use host1:port1,host2:port2,...")
        parser.error(f"Formato de --targets inválido: {e}")

    print(f"INFO [LB Main] Configurando LoadBalancerNode: name='{args.name}', port={args.port}, host_bind='{args.host}', ptime={args.ptime}")
    try:
        lb = LoadBalancerNode(
            name_tag=args.name,
            listen_port=args.port,
            host_to_bind=args.host,
            proc_time=args.ptime,
            target_hosts=target_hosts_list,
            target_ports=target_ports_list
        )
        lb.start()
    except Exception as e_init:
        print(f"ERRO FATAL [LB Main] Ao instanciar ou iniciar LoadBalancerNode: {e_init}", exc_info=True)
        exit(1)