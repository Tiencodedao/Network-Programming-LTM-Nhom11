using System;

namespace MyApp
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("=================================");
            Console.WriteLine("   UDP CLIENT-SERVER DEMO");
            Console.WriteLine("=================================\n");
            
            Console.WriteLine("Chọn chế độ:");
            Console.WriteLine("  [1] Client");
            Console.WriteLine("  [2] Server");
            Console.Write("\nNhập lựa chọn (1 hoặc 2): ");
            
            string choice = Console.ReadLine();
            Console.WriteLine();

            try
            {
                if (choice == "1")
                {
                    var client = new UdpClientApp();
                    string testData = new string('A', 50) + " Lorem ipsum dolor sit amet " + new string('B', 27900);
                    client.SendData(testData);
                }
                else if (choice == "2")
                {
                    var server = new UdpServerApp();
                    server.Start();
                }
                else
                {
                    Console.WriteLine("Lựa chọn không hợp lệ!");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\n LỖI: {ex.Message}");
            }

            Console.WriteLine("\n--- Nhấn Enter để thoát ---");
            Console.ReadLine();
        }
    }
}

