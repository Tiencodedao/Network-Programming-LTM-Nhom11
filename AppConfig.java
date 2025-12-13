public class AppConfig {
    // Sửa 9999 -> 8080
    public static final int PORT = 8080;
    
    public static final String HOST = "localhost";
    public static final int BUFFER = 1024 * 64; // 64KB Buffer
    
    // Senior Tuning: Tắt Nagle để Chat Realtime
    public static final boolean TCP_NO_DELAY = true;
}