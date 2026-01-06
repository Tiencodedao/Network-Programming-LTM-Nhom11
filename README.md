# Dự án Blog API

Đây là dự án API backend cho một hệ thống blog đơn giản.

## Hướng dẫn cài đặt và chạy dự án

### Yêu cầu
- Node.js 
-MYSQL WORKBENCH

### Các bước cài đặt
1.  Giải nén file `.zip`.
2.  Mở thư mục dự án bằng Terminal hoặc VS Code.
3.  Chạy lệnh `npm install` để cài đặt các thư viện cần thiết.
4.  Cài đặt và khởi động MYSQL WORKBENCH.
5.  Sử dụng MYSQL WORKBENCH, chạy file `database.sql` để tạo database `blog_db` và các bảng.
6.  Tạo một file `.env` ở thư mục gốc và điền các thông tin kết nối database của bạn.
7.  Chạy lệnh `npm run dev` để khởi động server.
8.  Server sẽ chạy tại `http://localhost:5000`.
9.  Import file `BlogAPI.postman_collection.json` vào Postman để kiểm tra các API.