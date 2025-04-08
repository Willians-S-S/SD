import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;

import java.io.*;
import java.net.InetSocketAddress;
import java.util.concurrent.*;

public class MestreServer {

    public static void main(String[] args) throws IOException {
        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
        server.createContext("/processar", new ProcessarHandler());
        server.setExecutor(Executors.newCachedThreadPool());
        System.out.println("Mestre rodando na porta 8080...");
        server.start();
    }

    static class ProcessarHandler implements HttpHandler {
        @Override
        public void handle(HttpExchange exchange) throws IOException {
            if (!exchange.getRequestMethod().equalsIgnoreCase("POST")) {
                exchange.sendResponseHeaders(405, -1); // Method Not Allowed
                return;
            }

            InputStream is = exchange.getRequestBody();
            String texto = new String(is.readAllBytes());
            is.close();

            ResultadoParcial letras = new ResultadoParcial();
            ResultadoParcial numeros = new ResultadoParcial();

            Thread t1 = new Thread(new WorkerThread("http://escravo1:8001/letras", letras, texto));
            Thread t2 = new Thread(new WorkerThread("http://escravo2:8002/numeros", numeros, texto));

            t1.start();
            t2.start();

            try {
                t1.join();
                t2.join();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }

            String respostaFinal = "Letras: " + letras.getResultado() + "\nNúmeros: " + numeros.getResultado();
            byte[] respostaBytes = respostaFinal.getBytes();

            exchange.sendResponseHeaders(200, respostaBytes.length);
            OutputStream os = exchange.getResponseBody();
            os.write(respostaBytes);
            os.close();
        }
    }
}
