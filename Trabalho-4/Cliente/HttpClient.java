import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;

public class HttpClient {
    public static String enviarTexto(String texto) throws IOException {
        URL url = new URL("http://localhost:8080/processar"); // ajuste conforme IP do mestre
        HttpURLConnection conn = (HttpURLConnection) url.openConnection();

        conn.setRequestMethod("POST");
        conn.setRequestProperty("Content-Type", "text/plain");
        conn.setDoOutput(true);

        try (OutputStream os = conn.getOutputStream()) {
            os.write(texto.getBytes());
        }

        BufferedReader in = new BufferedReader(new InputStreamReader(conn.getInputStream()));
        StringBuilder resposta = new StringBuilder();
        String linha;
        while ((linha = in.readLine()) != null) {
            resposta.append(linha).append("\n");
        }
        in.close();

        return resposta.toString();
    }
}
