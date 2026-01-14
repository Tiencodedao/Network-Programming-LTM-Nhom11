"""
DiscoveryService - Xử lý tìm kiếm phòng qua UDP broadcast
"""
import socket


class DiscoveryService:
    def __init__(self, discovery_port=9998):
        self.discovery_port = discovery_port

    def find_room(self, room_code, timeout=3):
        """
        Tìm phòng theo mã code

        Args:
            room_code: Mã phòng cần tìm
            timeout: Thời gian chờ phản hồi

        Returns:
            IP của server nếu tìm thấy, None nếu không tìm thấy
        """
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        udp_sock.settimeout(timeout)

        try:
            message = f"FIND|{room_code}"
            udp_sock.sendto(message.encode(), ('<broadcast>', self.discovery_port))

            data, addr = udp_sock.recvfrom(1024)
            response = data.decode()

            if response.startswith("FOUND|"):
                server_ip = response.split("|")[1]
                return server_ip

            return None

        except socket.timeout:
            return None
        except Exception as e:
            print(f"Discovery error: {e}")
            return None
        finally:
            udp_sock.close()

    def start_discovery_server(self, room_code, callback=None):
        """
        Khởi động server lắng nghe các yêu cầu tìm phòng

        Args:
            room_code: Mã phòng của server
            callback: Hàm callback khi có client tìm phòng
        """
        udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        udp_sock.bind(('0.0.0.0', self.discovery_port))

        while True:
            try:
                data, addr = udp_sock.recvfrom(1024)
                msg = data.decode()

                if msg.startswith("FIND|") and msg.split("|")[1] == room_code:
                    my_ip = self.get_local_ip()
                    udp_sock.sendto(f"FOUND|{my_ip}".encode(), addr)

                    if callback:
                        callback(addr)

            except Exception as e:
                print(f"Discovery server error: {e}")
                break

    @staticmethod
    def get_local_ip():
        """Lấy địa chỉ IP local"""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

