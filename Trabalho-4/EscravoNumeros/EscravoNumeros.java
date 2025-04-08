import com.sun.net.httpserver.*;

import java.io.*;
import java.net.InetSocketAddress;

public class EscravoNumeros {
    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(8002), 0);
        server.createContext("/numeros", new ContarNumerosHandler());
        server.setExecutor(null);
        System.out.println("Escravo 2 rodando na porta 8002...");
        server.start();
    }

    static class ContarNumerosHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!exchange.getRequestMethod().equalsIgnoreCase("POST")) {
                exchange.sendResponseHeaders(405, -1);
                return;
            }

            InputStream is = exchange.getRequestBody();
            String texto = new String(is.readAllBytes());
            is.close();

            long numeros = texto.chars().filter(Character::isDigit).count();
            String resposta = String.valueOf(numeros);

            byte[] respostaBytes = resposta.getBytes();
            exchange.sendResponseHeaders(200, respostaBytes.length);
            OutputStream os = exchange.getResponseBody();
            os.write(respostaBytes);
            os.close();
        }
    }
}
