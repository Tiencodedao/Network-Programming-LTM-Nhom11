package com.example.highload;

import org.glassfish.tyrus.server.Server;

public class ServerMain {
    public static void main(String[] args) {
        String host = "localhost";
        int port = 8080;
        String contextPath = "/";

        Server server = new Server(host, port, contextPath, null, ChatEndpoint.class);

        try {
            server.start();
            System.out.println("✅ WebSocket server started!");
            System.out.println("➡ Endpoint: ws://localhost:8080/ws/chat");
            System.out.println("Press ENTER to stop...");
            System.in.read();
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            server.stop();
            System.out.println("🛑 Server stopped.");
        }
    }
}
