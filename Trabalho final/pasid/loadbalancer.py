# loadbalancer.py
import time
import argparse
from socket_utils import send_message, start_generic_server
# Configurações serão passadas via argparse ou importadas de config.py

class LoadBalancerNode:
    def __init__(self, name_tag, listen_port, host, proc_time, target_hosts, target_ports):
        self.name_tag = name_tag
        self.listen_port = listen_port
        self.host = host
        self.processing_time = proc_time
        self.target_hosts = target_hosts
        self.target_ports = target_ports
        self.current_target_index = 0
        if not target_ports or len(target_hosts) != len(target_ports):
            raise ValueError("Hosts e Portas alvo do LoadBalancer mal configurados.")

    def handle_request(self, conn, addr, message_dict):
        data = message_dict['payload']
        timestamps = message_dict['timestamps']
        req_id = timestamps.get('request_id', 'N/A')

        # A entrada no LB é registrada pelo componente anterior ou pelo Source
        # Ex: timestamps[f'{self.name_tag}_entry'] já deve existir
        # ou timestamps[f'{self.name_tag}_entry_after_transit_S1_LB2'] para LB2

        entry_ts_key = next((k for k in timestamps if k.startswith(self.name_tag) and k.endswith("_entry")), None)
        if not entry_ts_key and self.name_tag.startswith("LoadBalancer2"): # Caso especial para LB2 vindo de S1
             entry_ts_key = f'{self.name_tag}_entry_after_transit_S1_LB2'
        
        if entry_ts_key not in timestamps: # Se LB1, a entrada é M2
            if self.name_tag.startswith("LoadBalancer1"):
                timestamps[f'{self.name_tag}_entry'] = timestamps.get('M2_source_sent_to_lb1', time.perf_counter())
                entry_ts_key = f'{self.name_tag}_entry'
            else: # fallback
                timestamps[f'{self.name_tag}_entry_fallback'] = time.perf_counter()
                entry_ts_key = f'{self.name_tag}_entry_fallback'


        print(f"[{self.name_tag}] Req-{req_id}: Recebeu de {addr}, dados: '{data}'. Distribuição: {self.processing_time:.2f}s.")
        
        time.sleep(self.processing_time)

        # Selecionar próximo serviço (Round Robin)
        selected_host = self.target_hosts[self.current_target_index]
        selected_port = self.target_ports[self.current_target_index]
        self.current_target_index = (self.current_target_index + 1) % len(self.target_ports)
        
        timestamps[f'{self.name_tag}_exit_distributed'] = time.perf_counter()
        duration = timestamps[f'{self.name_tag}_exit_distributed'] - timestamps[entry_ts_key]
        
        print(f"[{self.name_tag}] Req-{req_id}: Distribuição em {duration:.4f}s. Enviando para {selected_host}:{selected_port}.")

        next_message = {'payload': data, 'timestamps': timestamps} # LB não modifica o payload em si
        send_message(selected_host, selected_port, next_message)

    def start(self):
        start_generic_server(self.host, self.listen_port, self.handle_request, self.name_tag)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Balancer Node")
    parser.add_argument("--name", required=True, help="Nome/Tag do LB (ex: LoadBalancer1_Nó02)")
    parser.add_argument("--port", type=int, required=True, help="Porta de escuta")
    parser.add_argument("--host", default="127.0.0.1", help="Host de escuta")
    parser.add_argument("--ptime", type=float, required=True, help="Tempo de processamento do LB")
    parser.add_argument("--targets", required=True, help="Lista de alvos no formato host1:port1,host2:port2,...")
    
    args = parser.parse_args()

    target_hosts = []
    target_ports = []
    try:
        for target_str in args.targets.split(','):
            host, port_str = target_str.split(':')
            target_hosts.append(host)
            target_ports.append(int(port_str))
    except ValueError:
        parser.error("Formato de --targets inválido. Use host1:port1,host2:port2,...")

    lb = LoadBalancerNode(
        name_tag=args.name,
        listen_port=args.port,
        host=args.host,
        proc_time=args.ptime,
        target_hosts=target_hosts,
        target_ports=target_ports
    )
    lb.start()