// EscravoLetras.java
import com.sun.net.httpserver.*;

import java.io.*;
import java.net.InetSocketAddress;

public class EscravoLetras {
    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(8001), 0);
        server.createContext("/letras", new ContarLetrasHandler());
        server.setExecutor(null);
        System.out.println("Escravo 1 rodando na porta 8001...");
        server.start();
    }

    static class ContarLetrasHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!exchange.getRequestMethod().equalsIgnoreCase("POST")) {
                exchange.sendResponseHeaders(405, -1);
                return;
            }

            InputStream is = exchange.getRequestBody();
            String texto = new String(is.readAllBytes());
            is.close();

            long letras = texto.chars().filter(Character::isLetter).count();
            String resposta = String.valueOf(letras);

            byte[] respostaBytes = resposta.getBytes();
            exchange.sendResponseHeaders(200, respostaBytes.length);
            OutputStream os = exchange.getResponseBody();
            os.write(respostaBytes);
            os.close();
        }
    }
}
