import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.io.*;

public class ClienteGUI extends JFrame {
    private JTextArea textArea;
    private JButton btnEnviar;
    private JButton btnEscolherArquivo;
    private File arquivoSelecionado;

    public ClienteGUI() {
        setTitle("Cliente - Enviar Texto");
        setSize(500, 400);
        setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        setLocationRelativeTo(null);

        textArea = new JTextArea();
        textArea.setEditable(false);
        JScrollPane scroll = new JScrollPane(textArea);

        btnEscolherArquivo = new JButton("Escolher Arquivo");
        btnEnviar = new JButton("Enviar para o Mestre");

        btnEscolherArquivo.addActionListener(e -> escolherArquivo());
        btnEnviar.addActionListener(e -> enviarArquivo());

        JPanel panelBotoes = new JPanel();
        panelBotoes.add(btnEscolherArquivo);
        panelBotoes.add(btnEnviar);

        add(scroll, BorderLayout.CENTER);
        add(panelBotoes, BorderLayout.SOUTH);
    }

    private void escolherArquivo() {
        JFileChooser chooser = new JFileChooser();
        int resultado = chooser.showOpenDialog(this);

        if (resultado == JFileChooser.APPROVE_OPTION) {
            arquivoSelecionado = chooser.getSelectedFile();
            textArea.setText("Arquivo selecionado:\n" + arquivoSelecionado.getAbsolutePath());
        }
    }

    private void enviarArquivo() {
        if (arquivoSelecionado == null) {
            JOptionPane.showMessageDialog(this, "Selecione um arquivo primeiro.");
            return;
        }

        try {
            String conteudo = new String(java.nio.file.Files.readAllBytes(arquivoSelecionado.toPath()));
            String resposta = HttpClient.enviarTexto(conteudo);
            textArea.setText("Resposta do mestre:\n" + resposta);
        } catch (IOException ex) {
            ex.printStackTrace();
            JOptionPane.showMessageDialog(this, "Erro ao ler ou enviar o arquivo.");
        }
    }

    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            ClienteGUI gui = new ClienteGUI();
            gui.setVisible(true);
        });
    }
}
