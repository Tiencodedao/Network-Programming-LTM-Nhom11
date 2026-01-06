package com.example.highload;

import jakarta.websocket.*;

import java.net.URI;
import java.util.Scanner;

@ClientEndpoint
public class ClientMain {

    private static Session session;

    @OnOpen
    public void onOpen(Session s) {
        session = s;
        System.out.println("✅ Connected to server, session=" + s.getId());
    }

    @OnMessage
    public void onMessage(String message) {
        System.out.println("📩 Server: " + message);
    }

    @OnClose
    public void onClose(Session s, CloseReason reason) {
        System.out.println("❌ Closed: " + reason);
    }

    @OnError
    public void onError(Session s, Throwable t) {
        System.out.println("⚠️ Error: " + t.getMessage());
        t.printStackTrace();
    }

    public static void main(String[] args) throws Exception {
        URI uri = URI.create("ws://localhost:8080/ws/chat");

        WebSocketContainer container = ContainerProvider.getWebSocketContainer();
        container.connectToServer(ClientMain.class, uri);

        Scanner sc = new Scanner(System.in);
        while (true) {
            System.out.print("You: ");
            String msg = sc.nextLine();

            if ("exit".equalsIgnoreCase(msg)) {
                if (session != null && session.isOpen()) session.close();
                break;
            }

            if (session != null && session.isOpen()) {
                session.getAsyncRemote().sendText(msg);
            } else {
                System.out.println("⚠️ Session not open!");
            }
        }
    }
}
