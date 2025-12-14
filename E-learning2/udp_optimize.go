package main

import (
	"encoding/json"
	"fmt"
	"net"
	"os"
	"sync"
	"time"
)

// Cấu trúc gói dữ liệu (Packet structure)
type Packet struct {
	Seq          int    `json:"seq"`
	Data         string `json:"data"`
	IsRetransmit bool   `json:"is_retransmit"`
	MissingSeqs  []int  `json:"missing_seqs,omitempty"` // Chỉ dùng cho NACK
	Type         string `json:"type,omitempty"`         // Chỉ dùng cho NACK
}

// Cấu hình mạng
const (
	ServerAddr = "127.0.0.1:12000"
	ClientAddr = "127.0.0.1:12001"
	Delay      = 50 * time.Millisecond // Giả lập độ trễ mạng
)

// --- SERVER (Gửi Dữ Liệu và Xử lý Truyền Lại) ---
func serverSimulate(wg *sync.WaitGroup, startClient chan bool) {
	defer wg.Done()

	// Thiết lập UDP Listener
	serverUDPAddr, err := net.ResolveUDPAddr("udp", ServerAddr)
	if err != nil {
		fmt.Printf("SERVER: Lỗi giải quyết địa chỉ: %v\n", err)
		return
	}
	conn, err := net.ListenUDP("udp", serverUDPAddr)
	if err != nil {
		fmt.Printf("SERVER: Lỗi ListenUDP: %v\n", err)
		return
	}
	defer conn.Close()

	// Chờ Client sẵn sàng
	<-startClient

	fmt.Println(">>> SERVER: Khởi động.")

	originalData := make(map[int]string)
	for i := 1; i <= 10; i++ {
		originalData[i] = fmt.Sprintf("DATA_PACKET_%d", i)
	}

	clientUDPAddr, _ := net.ResolveUDPAddr("udp", ClientAddr)

	// 1. Gửi lần đầu (Initial Send)
	fmt.Println("\n[Vòng 1] Gửi ban đầu 10 gói:")
	for seqNum, data := range originalData {
		packet := Packet{Seq: seqNum, Data: data, IsRetransmit: false}
		packetBytes, _ := json.Marshal(packet)

		_, err := conn.WriteToUDP(packetBytes, clientUDPAddr)
		if err != nil {
			fmt.Printf("SERVER: Lỗi gửi gói %d: %v\n", seqNum, err)
			continue
		}
		fmt.Printf("  > Đã gửi gói: %d\n", seqNum)
		time.Sleep(Delay)
	}

	// 2. Chờ yêu cầu truyền lại (Wait for NACK)
	fmt.Println("\n[Vòng 2] Chờ NACK từ Client...")
	buffer := make([]byte, 1024)
	conn.SetReadDeadline(time.Now().Add(5 * time.Second)) // Thiết lập timeout

	n, _, err := conn.ReadFromUDP(buffer)
	if err != nil {
		if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
			fmt.Println("  < Không nhận được NACK trong thời gian chờ.")
		} else {
			fmt.Printf("SERVER: Lỗi đọc NACK: %v\n", err)
		}
	} else {
		var nackData Packet
		if err := json.Unmarshal(buffer[:n], &nackData); err == nil && nackData.Type == "NACK" {
			missingSeqs := nackData.MissingSeqs
			fmt.Printf("  < Đã nhận NACK. Yêu cầu truyền lại các gói: %v\n", missingSeqs)

			// 3. Truyền lại các gói bị thiếu (Selective Retransmission)
			fmt.Println("\n[Vòng 3] Truyền lại các gói bị thiếu:")
			for _, seqNum := range missingSeqs {
				data, ok := originalData[seqNum]
				if ok {
					packet := Packet{Seq: seqNum, Data: data, IsRetransmit: true}
					packetBytes, _ := json.Marshal(packet)

					conn.WriteToUDP(packetBytes, clientUDPAddr)
					fmt.Printf("  > Đã TRUYỀN LẠI gói: %d\n", seqNum)
					time.Sleep(Delay)
				}
			}
		}
	}

	fmt.Println("\n>>> SERVER: Đã tắt.")
}

// --- CLIENT (Nhận Dữ Liệu và Gửi NACK) ---
func clientSimulate(wg *sync.WaitGroup, startClient chan bool) {
	defer wg.Done()

	// Thiết lập UDP Listener
	clientUDPAddr, err := net.ResolveUDPAddr("udp", ClientAddr)
	if err != nil {
		fmt.Printf("CLIENT: Lỗi giải quyết địa chỉ: %v\n", err)
		return
	}
	conn, err := net.ListenUDP("udp", clientUDPAddr)
	if err != nil {
		fmt.Printf("CLIENT: Lỗi ListenUDP: %v\n", err)
		return
	}
	defer conn.Close()

	fmt.Println(">>> CLIENT: Khởi động.")
	startClient <- true // Báo hiệu cho Server bắt đầu gửi

	receivedData := make(map[int]string)
	expectedPackets := make(map[int]bool)
	for i := 1; i <= 10; i++ {
		expectedPackets[i] = true
	}

	buffer := make([]byte, 1024)

	// 1. Nhận gói lần đầu (Receiver Loop)
	fmt.Println("Nhận gói lần đầu (Giả lập mất gói 3 và 7):")

	// Nhận dữ liệu trong 3 giây
	startTime := time.Now()
	for time.Since(startTime) < 3*time.Second {
		conn.SetReadDeadline(time.Now().Add(500 * time.Millisecond))
		n, _, err := conn.ReadFromUDP(buffer)

		if err != nil {
			if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
				// Timeout khi không còn gói tin nào trong khoảng thời gian chờ
				break
			}
			// Bỏ qua các lỗi đọc khác
			continue
		}

		var packet Packet
		if err := json.Unmarshal(buffer[:n], &packet); err == nil {
			// Giả lập mất gói 3 và 7 trong lần gửi ban đầu
			if (packet.Seq == 3 || packet.Seq == 7) && !packet.IsRetransmit {
				fmt.Printf("  X BỎ QUA gói (mất): %d\n", packet.Seq)
				continue
			}

			if _, exists := receivedData[packet.Seq]; !exists {
				receivedData[packet.Seq] = packet.Data
				status := "Ban đầu"
				if packet.IsRetransmit {
					status = "Truyền lại"
				}
				fmt.Printf("  ✓ Đã nhận gói: %d (%s)\n", packet.Seq, status)
			}
		}
	}

	// 2. Phát hiện gói bị thiếu và Gửi NACK
	var missingSeqs []int
	for seqNum := 1; seqNum <= 10; seqNum++ {
		if _, exists := receivedData[seqNum]; !exists {
			missingSeqs = append(missingSeqs, seqNum)
		}
	}

	fmt.Printf("\n[Phát hiện] Tổng số gói đã nhận: %d\n", len(receivedData))
	fmt.Printf("[Phát hiện] Các gói bị thiếu: %v\n", missingSeqs)

	serverUDPAddr, _ := net.ResolveUDPAddr("udp", ServerAddr)

	if len(missingSeqs) > 0 {
		nackPacket := Packet{Type: "NACK", MissingSeqs: missingSeqs}
		nackBytes, _ := json.Marshal(nackPacket)
		conn.WriteToUDP(nackBytes, serverUDPAddr)
		fmt.Println("  > Đã gửi NACK yêu cầu truyền lại.")

		// 3. Chờ nhận các gói truyền lại
		fmt.Println("\nChờ nhận các gói truyền lại:")
		startTime = time.Now()
		for time.Since(startTime) < 3*time.Second {
			conn.SetReadDeadline(time.Now().Add(500 * time.Millisecond))
			n, _, err := conn.ReadFromUDP(buffer)

			if err != nil {
				if netErr, ok := err.(net.Error); ok && netErr.Timeout() {
					break
				}
				continue
			}

			var packet Packet
			if err := json.Unmarshal(buffer[:n], &packet); err == nil && packet.IsRetransmit {
				if _, exists := receivedData[packet.Seq]; !exists {
					receivedData[packet.Seq] = packet.Data
					fmt.Printf("  ✓ Đã nhận gói truyền lại: %d\n", packet.Seq)
				}
			}
		}
	}

	// 4. Kết quả cuối cùng
	var finalMissingSeqs []int
	for seqNum := 1; seqNum <= 10; seqNum++ {
		if _, exists := receivedData[seqNum]; !exists {
			finalMissingSeqs = append(finalMissingSeqs, seqNum)
		}
	}

	fmt.Println("\n--- KẾT QUẢ CUỐI CÙNG ---")
	if len(finalMissingSeqs) == 0 {
		fmt.Println("🎉 Tối ưu hóa thành công: Đã nhận đủ tất cả 10 gói sau khi truyền lại.")
	} else {
		fmt.Printf("⚠️ Vẫn còn thiếu các gói: %v\n", finalMissingSeqs)
	}

	fmt.Println("\n>>> CLIENT: Đã tắt.")
}

func main() {
	// Sử dụng WaitGroup để đợi cả Server và Client hoàn thành
	var wg sync.WaitGroup
	// Sử dụng channel để đảm bảo Client lắng nghe trước khi Server gửi
	startClient := make(chan bool)

	wg.Add(2)

	go clientSimulate(&wg, startClient)
	go serverSimulate(&wg, startClient)

	wg.Wait()
	os.Exit(0)
}
