public class ResultadoParcial {
    private String resultado = "0";

    public synchronized void setResultado(String resultado) {
        this.resultado = resultado;
    }

    public synchronized String getResultado() {
        return resultado;
    }
}
