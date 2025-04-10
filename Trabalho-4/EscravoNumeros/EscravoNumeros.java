import com.sun.net.httpserver.*; 
// Importa classes para criar e gerenciar um servidor HTTP

import java.io.*; 
// Importa classes para manipulação de entrada/saída

import java.net.InetSocketAddress; 
// Importa a classe para representar um endereço de socket (IP e porta)

public class EscravoNumeros {
    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(8002), 0);
        // Cria um servidor HTTP na porta 8002

        server.createContext("/numeros", new ContarNumerosHandler());
        // Define o endpoint "/numeros" e associa o handler para processar requisições

        server.setExecutor(null);
        // Usa o executor padrão para lidar com requisições

        System.out.println("Escravo 2 rodando na porta 8002...");
        // Mensagem indicando que o servidor está ativo

        server.start();
        // Inicia o servidor para aceitar conexões
    }

    static class ContarNumerosHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!exchange.getRequestMethod().equalsIgnoreCase("POST")) {
                exchange.sendResponseHeaders(405, -1);
                // Retorna o código HTTP 405 se o método não for POST
                return;
            }

            InputStream is = exchange.getRequestBody();
            // Obtém o corpo da requisição (texto enviado pelo mestre)

            String texto = new String(is.readAllBytes());
            // Lê o corpo da requisição como uma string

            is.close();
            // Fecha o fluxo de entrada para liberar recursos

            long numeros = texto.chars().filter(Character::isDigit).count();
            // Conta os caracteres que são dígitos numéricos no texto

            String resposta = String.valueOf(numeros);
            // Converte o resultado (número de dígitos) para uma string

            byte[] respostaBytes = resposta.getBytes();
            // Converte a resposta para um array de bytes

            exchange.sendResponseHeaders(200, respostaBytes.length);
            // Envia o código HTTP 200 (OK) e o tamanho da resposta

            OutputStream os = exchange.getResponseBody();
            os.write(respostaBytes);
            // Escreve a resposta no corpo da requisição

            os.close();
            // Fecha o fluxo de saída
        }
    }
}
