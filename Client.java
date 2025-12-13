import java.io.*;
import java.net.Socket;
import java.util.Scanner;

public class Client {
    public static void main(String[] args) {
        // Kết nối dùng thông số từ AppConfig
        try (Socket socket = new Socket(AppConfig.HOST, AppConfig.PORT)) {
            
            // Tối ưu Client: Gửi tin nhắn ngay lập tức
            socket.setTcpNoDelay(AppConfig.TCP_NO_DELAY); 
            
            System.out.println(">> Connected to Port " + AppConfig.PORT + "! Chat now...");

            // Thread nhận tin nhắn
            new Thread(() -> {
                try {
                    InputStream in = socket.getInputStream();
                    byte[] buffer = new byte[1024];
                    int read;
                    while ((read = in.read(buffer)) != -1) 
                        System.out.print(new String(buffer, 0, read));
                } catch (IOException e) { System.exit(0); }
            }).start();

            // Main Thread gửi tin nhắn
            PrintWriter out = new PrintWriter(socket.getOutputStream(), true);
            Scanner scanner = new Scanner(System.in);
            while (scanner.hasNextLine()) out.println(scanner.nextLine());

        } catch (IOException e) { 
            System.err.println("Connection Failed! Is Server running on " + AppConfig.PORT + "?");
        }
    }
}