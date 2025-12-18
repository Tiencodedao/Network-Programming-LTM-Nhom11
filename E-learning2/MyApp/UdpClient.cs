using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;

namespace MyApp
{
    class UdpClientApp
    {
        // === CẤU HÌNH ===
        private const string SERVER_IP = "127.0.0.1";
        private const int SERVER_PORT = 9000;
        private const int PACKET_SIZE = 1400;      // Kích thước mỗi gói
        private const int RETRY_MAX = 3;           // Số lần thử lại
        private const int TIMEOUT_MS = 1000;       // Timeout 1 giây
        
        private UdpClient client;
        private IPEndPoint serverEndPoint;
        private int totalSent = 0;
        private int totalRetry = 0;

        public UdpClientApp()
        {
            client = new UdpClient();
            client.Client.ReceiveTimeout = TIMEOUT_MS;
            serverEndPoint = new IPEndPoint(IPAddress.Parse(SERVER_IP), SERVER_PORT);
        }

        // Gửi dữ liệu chính
        public void SendData(string message)
        {
            Console.WriteLine("=== UDP CLIENT ===");
            Console.WriteLine($"Gửi đến: {SERVER_IP}:{SERVER_PORT}\n");

            byte[] data = Encoding.UTF8.GetBytes(message);
            int totalPackets = (int)Math.Ceiling((double)data.Length / PACKET_SIZE);
            
            Console.WriteLine($"Tổng dữ liệu: {data.Length} bytes");
            Console.WriteLine($"Chia thành: {totalPackets} gói\n");

            // Gửi từng gói
            for (int i = 0; i < totalPackets; i++)
            {
                int offset = i * PACKET_SIZE;
                int size = Math.Min(PACKET_SIZE, data.Length - offset);
                
                byte[] payload = new byte[size];
                Array.Copy(data, offset, payload, 0, size);
                
                SendPacket(i, payload);
                Thread.Sleep(50); 
            }

            // Gửi gói kết thúc
            SendPacket(-1, Encoding.UTF8.GetBytes("END"));
            
            ShowStats();
            client.Close();
        }

        // Gửi 1 gói với retry
        private void SendPacket(int seqNum, byte[] payload)
        {
            byte[] packet = CreatePacket(seqNum, payload);
            
            for (int retry = 0; retry < RETRY_MAX; retry++)
            {
                try
                {
                    // Gửi gói
                    client.Send(packet, packet.Length, serverEndPoint);
                    Console.Write($"[{seqNum,3}] Gửi {packet.Length,4}B");

                    // Đợi ACK
                    IPEndPoint remoteEP = new IPEndPoint(IPAddress.Any, 0);
                    byte[] ackData = client.Receive(ref remoteEP);
                    int ackSeq = GetSeqNumber(ackData);

                    if (ackSeq == seqNum)
                    {
                        Console.WriteLine(" ✓ OK");
                        totalSent++;
                        if (retry > 0) totalRetry += retry;
                        return;
                    }
                }
                catch (SocketException)
                {
                    Console.WriteLine($" ✗ Timeout (retry {retry + 1}/{RETRY_MAX})");
                }
            }
            
            Console.WriteLine($" ✗ FAILED after {RETRY_MAX} retries");
        }

        // Tạo gói tin: [4 bytes seq] + [payload]
        private byte[] CreatePacket(int seqNum, byte[] payload)
        {
            byte[] packet = new byte[4 + payload.Length];
            byte[] seqBytes = BitConverter.GetBytes(seqNum);
            
            Array.Copy(seqBytes, 0, packet, 0, 4);
            Array.Copy(payload, 0, packet, 4, payload.Length);
            
            return packet;
        }

        // Lấy sequence number từ ACK
        private int GetSeqNumber(byte[] data)
        {
            if (data.Length < 4) return -999;
            return BitConverter.ToInt32(data, 0);
        }

        // Hiển thị thống kê
        private void ShowStats()
        {
            Console.WriteLine("\n=== THỐNG KÊ ===");
            Console.WriteLine($"Gói gửi thành công: {totalSent}");
            Console.WriteLine($"Số lần retry: {totalRetry}");
            
            if (totalSent > 0)
            {
                double retryRate = (double)totalRetry / totalSent * 100;
                Console.WriteLine($"Tỷ lệ retry: {retryRate:F2}%");
            }
        }

    }
}
