import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;

public class WorkerThread implements Runnable {
    private final String urlEscravo;
    private final ResultadoParcial resultado;
    private final String texto;

    public WorkerThread(String urlEscravo, ResultadoParcial resultado, String texto) {
        this.urlEscravo = urlEscravo;
        this.resultado = resultado;
        this.texto = texto;
    }

    @Override
    public void run() {
        try {
            URL url = new URL(urlEscravo); // Cria a URL para o escravo
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST"); // Define o método HTTP como POST
            conn.setDoOutput(true); // Permite enviar dados no corpo da requisição
            conn.setRequestProperty("Content-Type", "text/plain"); // Define o tipo de conteúdo como texto simples

            try (OutputStream os = conn.getOutputStream()) {
                os.write(texto.getBytes()); // Envia o texto para o escravo
            }

            BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String response = reader.readLine(); // Lê a resposta do escravo
            resultado.setResultado(response); // Armazena o resultado na instância de ResultadoParcial

        } catch (IOException e) {
            resultado.setResultado("Erro"); // Define o resultado como "Erro" em caso de falha
            e.printStackTrace(); // Exibe o erro no console
        }
    }
}