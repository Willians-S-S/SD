public class ResultadoParcial {
    private String resultado = "0"; // Armazena o resultado parcial (inicialmente "0")

    public synchronized void setResultado(String resultado) {
        this.resultado = resultado; // Atualiza o resultado de forma thread-safe
    }

    public synchronized String getResultado() {
        return resultado; // Retorna o resultado de forma thread-safe
    }
}
