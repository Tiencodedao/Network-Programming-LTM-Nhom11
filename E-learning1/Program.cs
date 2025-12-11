using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

public class TCPServer
{
    public static void Main(string[] args)
    {
        try
        {
            
            TcpListener serverSocket = new TcpListener(IPAddress.Any, 8080);
            serverSocket.Start();
            Console.WriteLine("Server dang lang nghe cong 8080");

            TcpClient clientSocket = serverSocket.AcceptTcpClient();
            Console.WriteLine("Ket noi voi client: " + ((IPEndPoint)clientSocket.Client.RemoteEndPoint).Address);

            clientSocket.ReceiveBufferSize = 65536;
            clientSocket.SendBufferSize = 65536;

            NetworkStream stream = clientSocket.GetStream();

            byte[] buffer = new byte[1024];
            int bytesRead;

            while ((bytesRead = stream.Read(buffer, 0, buffer.Length)) != 0)
            {
                Console.WriteLine("Nhan du lieu: " + Encoding.UTF8.GetString(buffer, 0, bytesRead));
                stream.Write(buffer, 0, bytesRead);
            }

            clientSocket.Close();
            serverSocket.Stop();
        }
        catch (Exception e)
        {
            Console.WriteLine(e.Message);
        }
    }
}