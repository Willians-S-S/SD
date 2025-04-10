import com.sun.net.httpserver.HttpServer; // Classe para criar um servidor HTTP embutido
import com.sun.net.httpserver.HttpExchange; // Representa uma troca de requisição/resposta HTTP
import com.sun.net.httpserver.HttpHandler; // Interface para lidar com requisições HTTP

import java.io.*; // Importa classes para manipulação de entrada/saída
import java.net.InetSocketAddress; // Classe para representar um endereço de socket (IP e porta)
import java.util.concurrent.*; // Importa classes para manipulação de threads e executores

public class MestreServer {

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0); 
        // Cria um servidor HTTP na porta 8080

        server.createContext("/processar", new ProcessarHandler()); 
        // Define o endpoint "/processar" e associa o handler para processar requisições

        server.setExecutor(Executors.newCachedThreadPool()); 
        // Configura um executor com um pool de threads dinâmico para lidar com múltiplas requisições

        System.out.println("Mestre rodando na porta 8080..."); 
        // Mensagem indicando que o servidor está ativo

        server.start(); 
        // Inicia o servidor para aceitar conexões
    }

    static class ProcessarHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!exchange.getRequestMethod().equalsIgnoreCase("POST")) {
                exchange.sendResponseHeaders(405, -1); // Retorna o código HTTP 405 se o método não for POST
                return;
            }

            InputStream is = exchange.getRequestBody(); 
            // Obtém o corpo da requisição (texto enviado pelo cliente)

            String texto = new String(is.readAllBytes()); 
            // Lê o corpo da requisição como uma string

            is.close(); 
            // Fecha o fluxo de entrada para liberar recursos

            ResultadoParcial letras = new ResultadoParcial(); 
            // Objeto para armazenar o resultado parcial de letras

            ResultadoParcial numeros = new ResultadoParcial(); 
            // Objeto para armazenar o resultado parcial de números

            Thread t1 = new Thread(new WorkerThread("http://escravo1:8001/letras", letras, texto)); 
            // Cria uma thread para enviar o texto ao EscravoLetras

            Thread t2 = new Thread(new WorkerThread("http://escravo2:8002/numeros", numeros, texto)); 
            // Cria uma thread para enviar o texto ao EscravoNumeros

            t1.start(); 
            // Inicia a thread que processa letras

            t2.start(); 
            // Inicia a thread que processa números

            try {
                t1.join(); // Aguarda a conclusão da thread que processa letras
                t2.join(); // Aguarda a conclusão da thread que processa números
            } catch (InterruptedException e) {
                e.printStackTrace(); // Trata interrupções durante a espera das threads
            }

            String respostaFinal = "Letras: " + letras.getResultado() + "\nNúmeros: " + numeros.getResultado();
            // Combina os resultados parciais em uma única resposta

            byte[] respostaBytes = respostaFinal.getBytes();

            exchange.sendResponseHeaders(200, respostaBytes.length); // Envia o código HTTP 200 (OK) e o tamanho da resposta
            OutputStream os = exchange.getResponseBody();
            os.write(respostaBytes); // Escreve a resposta no corpo da requisição
            os.close(); // Fecha o fluxo de saída
        }
    }
}
