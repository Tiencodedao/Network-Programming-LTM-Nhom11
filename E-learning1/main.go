package main

import (
	"fmt"
	"io"
	"net"
)

const PORT = ":8080"

func handleConnection(conn net.Conn) {
	if tcpConn, ok := conn.(*net.TCPConn); ok {
		tcpConn.SetNoDelay(true)
	}
	defer conn.Close()

	fmt.Printf("Phục vụ Client: %s\n", conn.RemoteAddr().String())
	bytes, err := io.Copy(conn, conn)

	if err != nil && err != io.EOF {
		fmt.Printf("Lỗi xử lý kết nối: %v\n", err)
		return
	}

	fmt.Printf("Đóng kết nối với %s. Tổng byte được chuyển: %d\n", conn.RemoteAddr().String(), bytes)
}

func main() {
	listener, err := net.Listen("tcp", PORT)
	if err != nil {
		fmt.Printf("Lỗi lắng nghe: %v\n", err)
		return
	}
	defer listener.Close()

	fmt.Printf("TCP Server đang chạy trên cổng %s...\n", PORT)

	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Printf("Lỗi chấp nhận kết nối: %v\n", err)
			continue
		}
		go handleConnection(conn)
	}
}
