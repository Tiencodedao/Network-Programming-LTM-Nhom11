package com.example.highload;

import jakarta.websocket.*;
import jakarta.websocket.server.ServerEndpoint;

import java.io.IOException;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;

@ServerEndpoint("/ws/chat")
public class ChatEndpoint {

    // Lưu sessions để broadcast (hỗ trợ nhiều client)
    private static final Set<Session> sessions = ConcurrentHashMap.newKeySet();

    @OnOpen
    public void onOpen(Session session) {
        sessions.add(session);
        System.out.println("✅ Client connected: " + session.getId());
        sendSafe(session, "Welcome! session=" + session.getId());
    }

    @OnMessage
    public void onMessage(String message, Session session) {
        System.out.println("📩 " + session.getId() + " -> " + message);

        // Echo lại cho chính client (như bạn đang test)
        sendSafe(session, "Server received: " + message);

        // (Tuỳ chọn) broadcast cho tất cả client:
        // broadcast("[" + session.getId() + "]: " + message);
    }

    @OnClose
    public void onClose(Session session, CloseReason reason) {
        sessions.remove(session);
        System.out.println("❌ Client disconnected: " + session.getId() + " reason=" + reason);
    }

    @OnError
    public void onError(Session session, Throwable t) {
        System.out.println("⚠️ Error session=" + (session != null ? session.getId() : "null"));
        t.printStackTrace();
    }

    private static void broadcast(String msg) {
        for (Session s : sessions) {
            sendSafe(s, msg);
        }
    }

    private static void sendSafe(Session session, String msg) {
        if (session == null || !session.isOpen()) return;
        // async để chịu tải tốt hơn (không block)
        session.getAsyncRemote().sendText(msg);
    }
}
