# socket_utils.py
import socket
import json
import struct
import time

HEADER_SIZE = 8  # Usar 8 bytes para enviar o tamanho da mensagem

def send_message(host, port, message_dict, max_retries=3, retry_delay=0.5):
    """Envia um dicionário como uma mensagem JSON via socket com retentativas."""
    attempt = 0
    while attempt < max_retries:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                # print(f"DEBUG send_message: Tentando conectar a {host}:{port} (tentativa {attempt + 1})")
                s.connect((host, port))
                serialized_message = json.dumps(message_dict).encode('utf-8')
                message_length = len(serialized_message)
                header = struct.pack('>Q', message_length)

                s.sendall(header)
                s.sendall(serialized_message)
                # print(f"DEBUG send_message: Enviado para {host}:{port}, header: {message_length}")
                return True # Sucesso
        except ConnectionRefusedError:
            print(f"ERRO send_message: Conexão recusada ao tentar enviar para {host}:{port} (tentativa {attempt + 1}/{max_retries}).")
        except socket.timeout:
            print(f"ERRO send_message: Timeout ao tentar conectar/enviar para {host}:{port} (tentativa {attempt + 1}/{max_retries}).")
        except Exception as e:
            print(f"ERRO send_message: Falha ao enviar mensagem para {host}:{port} (tentativa {attempt + 1}/{max_retries}): {e}")
        
        attempt += 1
        if attempt < max_retries:
            # print(f"DEBUG send_message: Aguardando {retry_delay}s antes da próxima tentativa para {host}:{port}.")
            time.sleep(retry_delay)
        else:
            print(f"ERRO send_message: Falha definitiva ao enviar para {host}:{port} após {max_retries} tentativas.")
    return False # Falha após todas as tentativas

def receive_message(conn):
    """Recebe uma mensagem JSON via socket (conexão já estabelecida)."""
    try:
        conn.settimeout(10.0) # Timeout para recebimento do header e dados
        header_data = conn.recv(HEADER_SIZE)
        if not header_data:
            # print("DEBUG receive_message: Conexão fechada pelo peer (sem header).")
            return None
        if len(header_data) < HEADER_SIZE:
            print(f"ERRO receive_message: Header incompleto recebido ({len(header_data)} bytes). Esperado {HEADER_SIZE}.")
            return None
        message_length = struct.unpack('>Q', header_data)[0]
        
        if message_length == 0: # Mensagem vazia (mas válida)
             return {}

        if message_length > 10 * 1024 * 1024: # Limite de 10MB para mensagem
            print(f"ERRO receive_message: Tamanho da mensagem ({message_length} bytes) excede o limite.")
            return None

        data_buffer = b""
        remaining_length = message_length
        while remaining_length > 0:
            chunk = conn.recv(min(4096, remaining_length))
            if not chunk:
                print("ERRO receive_message: Conexão fechada inesperadamente ao receber dados da mensagem.")
                return None
            data_buffer += chunk
            remaining_length -= len(chunk)
            
        if len(data_buffer) != message_length:
            print(f"ERRO receive_message: Tamanho dos dados recebidos ({len(data_buffer)}) não corresponde ao esperado ({message_length}).")
            return None

        message_str = data_buffer.decode('utf-8')
        return json.loads(message_str)
    except struct.error as e:
        print(f"ERRO receive_message: Ao desempacotar header: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"ERRO receive_message: Ao decodificar JSON: {e}. Dados: {data_buffer[:200].decode('utf-8', errors='ignore')}") # Log preview
        return None
    except socket.timeout:
        print("ERRO receive_message: Timeout durante o recebimento da mensagem.")
        return None
    except Exception as e:
        print(f"ERRO receive_message: Inesperado ao receber mensagem: {e}")
        return None

def start_generic_server(host, port, handler_function, node_name="Servidor"):
    """
    Inicia um servidor TCP genérico que escuta em host:port
    e chama handler_function para cada mensagem recebida.
    handler_function deve aceitar (conn, addr, received_message_dict).
    """
    print(f"INFO [{node_name}] Tentando iniciar servidor em {host}:{port}")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((host, port))
            s.listen(10) # Aumentar backlog se necessário
            print(f"INFO [{node_name}] escutando em {host}:{port}")
            while True:
                conn = None # Garantir que conn seja definido
                try:
                    conn, addr = s.accept()
                    # print(f"DEBUG [{node_name}] Conexão de {addr}")
                    with conn: # Garante que a conexão seja fechada
                        message_dict = receive_message(conn)
                        if message_dict is not None: # Checa se não é None (erro no receive_message)
                            # print(f"DEBUG [{node_name}] Mensagem recebida de {addr}: {str(message_dict)[:200]}")
                            handler_function(conn, addr, message_dict)
                        else:
                            print(f"WARN [{node_name}] Nenhuma mensagem válida recebida ou conexão fechada por {addr}.")
                except socket.timeout: # Timeout no accept (pouco provável com listen sem timeout)
                    # print(f"DEBUG [{node_name}] Timeout no accept, continuando...")
                    continue
                except Exception as e_conn:
                    print(f"ERRO [{node_name}] Ao lidar com conexão de {addr if 'addr' in locals() else 'desconhecido'}: {e_conn}")
                    if conn: # Tenta fechar a conexão se ela foi estabelecida
                        try:
                            conn.close()
                        except Exception as e_close:
                            print(f"ERRO [{node_name}] Ao tentar fechar conexão com erro: {e_close}")
    except KeyboardInterrupt:
        print(f"\nINFO [{node_name}] Servidor em {host}:{port} encerrado por usuário.")
    except OSError as e_os:
        print(f"ERRO FATAL [{node_name}] OSError ao tentar iniciar servidor em {host}:{port} (porta pode estar em uso?): {e_os}")
    except Exception as e_main:
        print(f"ERRO FATAL [{node_name}] Inesperado no loop principal do servidor em {host}:{port}: {e_main}")