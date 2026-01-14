using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Collections.Generic;

namespace MyApp
{
    class UdpServerApp
    {
        // === CẤU HÌNH ===
        private const string SERVER_IP = "127.0.0.1";
        private const int SERVER_PORT = 9000;
        private const int BUFFER_SIZE = 2048;
        
        private Socket socket;
        private Dictionary<int, byte[]> receivedPackets;
        private List<byte> assembledData;
        
        private int expectedSeq = 0;
        private int totalReceived = 0;
        private int outOfOrder = 0;
        private int duplicates = 0;

        public UdpServerApp()
        {
            socket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);
            socket.Bind(new IPEndPoint(IPAddress.Parse(SERVER_IP), SERVER_PORT));
            
            receivedPackets = new Dictionary<int, byte[]>();
            assembledData = new List<byte>();
        }

        // Bắt đầu lắng nghe
        public void Start()
        {
            Console.WriteLine("=== UDP SERVER ===");
            Console.WriteLine($"Đang lắng nghe tại: {SERVER_IP}:{SERVER_PORT}\n");

            byte[] buffer = new byte[BUFFER_SIZE];
            EndPoint clientEP = new IPEndPoint(IPAddress.Any, 0);

            try
            {
                while (true)
                {
                    // Nhận gói
                    int bytesReceived = socket.ReceiveFrom(buffer, ref clientEP);
                    
                    if (bytesReceived < 4) continue; // Gói quá nhỏ

                    // Lấy sequence number
                    int seqNum = BitConverter.ToInt32(buffer, 0);
                    
                    // Lấy payload
                    int payloadSize = bytesReceived - 4;
                    byte[] payload = new byte[payloadSize];
                    Array.Copy(buffer, 4, payload, 0, payloadSize);

                    Console.Write($"[{seqNum,3}] Nhận {bytesReceived,4}B");

                    // Kiểm tra gói kết thúc
                    if (seqNum == -1)
                    {
                        Console.WriteLine(" - Gói kết thúc");
                        SendAck(seqNum, clientEP);
                        break;
                    }

                    // Xử lý gói dữ liệu
                    if (!receivedPackets.ContainsKey(seqNum))
                    {
                        receivedPackets[seqNum] = payload;
                        
                        if (seqNum != expectedSeq)
                        {
                            Console.WriteLine($" - Ngoài thứ tự (đang chờ {expectedSeq})");
                            outOfOrder++;
                        }
                        else
                        {
                            Console.WriteLine(" ✓");
                        }
                    }
                    else
                    {
                        Console.WriteLine(" - Trùng lặp");
                        duplicates++;
                    }

                    // Gửi ACK
                    SendAck(seqNum, clientEP);

                    // Ghép các gói theo thứ tự
                    while (receivedPackets.ContainsKey(expectedSeq))
                    {
                        byte[] data = receivedPackets[expectedSeq];
                        assembledData.AddRange(data);
                        receivedPackets.Remove(expectedSeq);
                        totalReceived++;
                        expectedSeq++;
                    }
                }

                ShowStats();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n LỖI: {ex.Message}");
            }
            finally
            {
                socket.Close();
            }
        }

        // Gửi ACK
        private void SendAck(int seqNum, EndPoint clientEP)
        {
            byte[] ackData = BitConverter.GetBytes(seqNum);
            socket.SendTo(ackData, clientEP);
        }

        // Hiển thị thống kê
        private void ShowStats()
        {
            Console.WriteLine("\n=== THỐNG KÊ ===");
            Console.WriteLine($"Tổng gói nhận: {totalReceived}");
            Console.WriteLine($"Ngoài thứ tự: {outOfOrder}");
            Console.WriteLine($"Trùng lặp: {duplicates}");
            Console.WriteLine($"Còn trong buffer: {receivedPackets.Count}");
            Console.WriteLine($"Tổng dữ liệu: {assembledData.Count} bytes");

            // Hiển thị preview dữ liệu
            if (assembledData.Count > 0)
            {
                int previewLen = Math.Min(100, assembledData.Count);
                string preview = Encoding.UTF8.GetString(assembledData.ToArray(), 0, previewLen);
                Console.WriteLine($"\nPreview (100 ký tự đầu):\n{preview}...");
            }
        }

    }
}
