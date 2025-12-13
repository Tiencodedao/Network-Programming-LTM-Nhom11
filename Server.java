import java.io.IOException;
import java.net.InetSocketAddress;
import java.net.StandardSocketOptions;
import java.nio.ByteBuffer;
import java.nio.channels.*;
import java.util.*;

public class Server {
    private Selector selector;

    public static void main(String[] args) throws IOException {
        new Server().run();
    }

    private void run() throws IOException {
        selector = Selector.open();
        ServerSocketChannel server = ServerSocketChannel.open();
        
        // Lấy PORT 8080 từ AppConfig
        server.bind(new InetSocketAddress(AppConfig.PORT));
        server.configureBlocking(false); // Quan trọng: Chế độ Non-blocking
        server.register(selector, SelectionKey.OP_ACCEPT);

        System.out.println(">> SENIOR SERVER listening on port " + AppConfig.PORT);

        while (true) {
            selector.select(); // Block chờ sự kiện (Hiệu quả CPU)
            Iterator<SelectionKey> keys = selector.selectedKeys().iterator();

            while (keys.hasNext()) {
                SelectionKey key = keys.next();
                keys.remove();

                if (!key.isValid()) continue;
                try {
                    if (key.isAcceptable()) accept(key);
                    else if (key.isReadable()) read(key);
                } catch (IOException e) { key.cancel(); }
            }
        }
    }

    private void accept(SelectionKey key) throws IOException {
        ServerSocketChannel server = (ServerSocketChannel) key.channel();
        SocketChannel client = server.accept();
        client.configureBlocking(false);
        
        // --- SENIOR TCP TUNING (Lấy từ AppConfig) ---
        client.setOption(StandardSocketOptions.TCP_NODELAY, AppConfig.TCP_NO_DELAY);
        client.setOption(StandardSocketOptions.SO_RCVBUF, AppConfig.BUFFER);
        
        client.register(selector, SelectionKey.OP_READ);
        broadcast("System: Client " + client.getRemoteAddress() + " joined.", client);
    }

    private void read(SelectionKey key) throws IOException {
        SocketChannel client = (SocketChannel) key.channel();
        ByteBuffer buffer = ByteBuffer.allocate(1024);
        if (client.read(buffer) == -1) { 
            client.close(); 
            return; 
        }
        
        String msg = new String(buffer.array()).trim();
        if (!msg.isEmpty()) broadcast(client.getRemoteAddress() + ": " + msg, client);
    }

    private void broadcast(String msg, SocketChannel sender) throws IOException {
        ByteBuffer buffer = ByteBuffer.wrap((msg + "\n").getBytes());
        for (SelectionKey key : selector.keys()) {
            Channel target = key.channel();
            if (target instanceof SocketChannel && target != sender) {
                ((SocketChannel) target).write(buffer);
                buffer.rewind();
            }
        }
    }
}