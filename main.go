package main

import (
	"fmt"
	"io"
	"net"
)

const PORT = ":8080"

// Hàm xử lý kết nối Client. Được chạy trong một Goroutine riêng biệt.
func handleConnection(conn net.Conn) {
	// 1. Kích hoạt TCP_NODELAY (Tối ưu hóa độ trễ)
	// Ngăn Nagle's Algorithm đóng gói các gói nhỏ, đảm bảo phản hồi ngay lập tức.
	if tcpConn, ok := conn.(*net.TCPConn); ok {
		tcpConn.SetNoDelay(true)
	}

	// Đảm bảo đóng kết nối khi hàm kết thúc
	defer conn.Close()

	fmt.Printf("Phục vụ Client: %s\n", conn.RemoteAddr().String())

	// 2. Xử lý I/O bất đồng bộ bằng cách sao chép dữ liệu
	// io.Copy sao chép dữ liệu từ nguồn (Client) sang đích (Client)
	// Hàm này sẽ chặn cho đến khi kết nối bị đóng hoặc gặp lỗi I/O.
	bytes, err := io.Copy(conn, conn)

	if err != nil && err != io.EOF {
		fmt.Printf("Lỗi xử lý kết nối: %v\n", err)
		return
	}

	fmt.Printf("Đóng kết nối với %s. Tổng byte được chuyển: %d\n", conn.RemoteAddr().String(), bytes)
}

func main() {
	// Lắng nghe các kết nối TCP trên cổng 8080
	listener, err := net.Listen("tcp", PORT)
	if err != nil {
		fmt.Printf("Lỗi lắng nghe: %v\n", err)
		return
	}
	defer listener.Close()

	fmt.Printf("TCP Server đang chạy trên cổng %s...\n", PORT)

	for {
		// Chấp nhận một kết nối mới
		conn, err := listener.Accept()
		if err != nil {
			fmt.Printf("Lỗi chấp nhận kết nối: %v\n", err)
			continue
		}

		// Tạo một Goroutine mới để xử lý kết nối này.
		// Đây là cơ chế tối ưu hóa chính của Go.
		go handleConnection(conn)
	}
}
