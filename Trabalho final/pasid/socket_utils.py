# socket_utils.py
import socket
import json
import struct

HEADER_SIZE = 8  # Usar 8 bytes para enviar o tamanho da mensagem

def send_message(host, port, message_dict):
    """Envia um dicionário como uma mensagem JSON via socket."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            serialized_message = json.dumps(message_dict).encode('utf-8')
            message_length = len(serialized_message)
            header = struct.pack('>Q', message_length) # Envia tamanho como unsigned long long (8 bytes)
            
            s.sendall(header)
            s.sendall(serialized_message)
            # print(f"DEBUG: Sent to {host}:{port}, header: {message_length}, msg_preview: {serialized_message[:50]}")
    except ConnectionRefusedError:
        print(f"ERRO: Conexão recusada ao tentar enviar para {host}:{port}. O servidor está em execução?")
    except Exception as e:
        print(f"ERRO ao enviar mensagem para {host}:{port}: {e}")


def receive_message(conn):
    """Recebe uma mensagem JSON via socket (conexão já estabelecida)."""
    try:
        # Primeiro, recebe o header para saber o tamanho da mensagem
        header_data = conn.recv(HEADER_SIZE)
        if not header_data:
            return None # Conexão fechada
        message_length = struct.unpack('>Q', header_data)[0]
        
        # Agora recebe a mensagem completa
        data_buffer = b""
        remaining_length = message_length
        while remaining_length > 0:
            chunk = conn.recv(min(4096, remaining_length)) # Recebe em pedaços
            if not chunk:
                print("ERRO: Conexão fechada inesperadamente ao receber dados da mensagem.")
                return None
            data_buffer += chunk
            remaining_length -= len(chunk)
            
        if len(data_buffer) != message_length:
            print(f"ERRO: Tamanho da mensagem recebida ({len(data_buffer)}) não corresponde ao esperado ({message_length}).")
            return None

        message_str = data_buffer.decode('utf-8')
        return json.loads(message_str)
    except struct.error as e:
        print(f"ERRO ao desempacotar header: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERRO ao decodificar JSON: {e}. Dados recebidos: {data_buffer.decode('utf-8', errors='ignore')}")
        return None
    except Exception as e:
        print(f"ERRO ao receber mensagem: {e}")
        return None

def start_generic_server(host, port, handler_function, node_name="Servidor"):
    """
    Inicia um servidor TCP genérico que escuta em host:port
    e chama handler_function para cada mensagem recebida.
    handler_function deve aceitar (conn, addr, received_message_dict).
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reusar endereço rapidamente
        s.bind((host, port))
        s.listen()
        print(f"[{node_name}] escutando em {host}:{port}")
        try:
            while True:
                conn, addr = s.accept()
                # print(f"[{node_name}] Conexão de {addr}")
                with conn:
                    message_dict = receive_message(conn)
                    if message_dict:
                        # print(f"[{node_name}] Mensagem recebida de {addr}: {message_dict}")
                        handler_function(conn, addr, message_dict) # Passa a conexão se precisar responder
                    else:
                        print(f"[{node_name}] Nenhuma mensagem válida recebida ou conexão fechada por {addr}.")
        except KeyboardInterrupt:
            print(f"\n[{node_name}] Servidor encerrado.")
        except Exception as e:
            print(f"[{node_name}] Erro no servidor: {e}")