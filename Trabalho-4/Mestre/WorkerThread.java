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
            URL url = new URL(urlEscravo);
            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("POST");
            conn.setDoOutput(true);
            conn.setRequestProperty("Content-Type", "text/plain");

            try (OutputStream os = conn.getOutputStream()) {
                os.write(texto.getBytes());
            }

            BufferedReader reader = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String response = reader.readLine();
            resultado.setResultado(response);

        } catch (IOException e) {
            resultado.setResultado("Erro");
            e.printStackTrace();
        }
    }
}