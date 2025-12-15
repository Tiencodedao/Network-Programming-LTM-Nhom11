#define _WINSOCK_DEPRECATED_NO_WARNINGS

#include <winsock2.h>
#include <ws2tcpip.h>
#include <iostream>
#include <vector>

#pragma comment(lib, "ws2_32.lib")

int main() {
    WSADATA wsa;
    WSAStartup(MAKEWORD(2, 2), &wsa);

    SOCKET server = socket(AF_INET, SOCK_STREAM, 0);

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = INADDR_ANY;
    addr.sin_port = htons(9000);

    bind(server, (sockaddr*)&addr, sizeof(addr));
    listen(server, SOMAXCONN);

    std::cout << "Echo Server running on port 9000...\n";

    fd_set master_set, read_set;
    FD_ZERO(&master_set);
    FD_SET(server, &master_set);

    std::vector<SOCKET> clients;

    while (true) {
        read_set = master_set;
        select(0, &read_set, nullptr, nullptr, nullptr);

        if (FD_ISSET(server, &read_set)) {
            SOCKET client = accept(server, nullptr, nullptr);
            FD_SET(client, &master_set);
            clients.push_back(client);
            std::cout << "New client connected\n";
        }

        for (auto it = clients.begin(); it != clients.end();) {
            SOCKET client = *it;
            if (FD_ISSET(client, &read_set)) {
                char buffer[1024];
                int bytes = recv(client, buffer, sizeof(buffer), 0);

                if (bytes <= 0) {
                    closesocket(client);
                    FD_CLR(client, &master_set);
                    it = clients.erase(it);
                    std::cout << "Client disconnected\n";
                    continue;
                }
                send(client, buffer, bytes, 0);
            }
            ++it;
        }
    }

    closesocket(server);
    WSACleanup();
    return 0;
}
