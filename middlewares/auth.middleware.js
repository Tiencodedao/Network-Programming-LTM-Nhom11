const jwt = require('jsonwebtoken');
const config = require('../config/app.config');

const authMiddleware = (req, res, next) => {
    let token;

    // 1. Lấy token từ Header (Bearer Token)
    if (req.headers.authorization && req.headers.authorization.startsWith('Bearer')) {
        token = req.headers.authorization.split(' ')[1];
    }

    // 2. Nếu không có token -> Báo lỗi 401
    if (!token) {
        return res.status(401).json({ success: false, message: "Bạn chưa đăng nhập (Thiếu Token)" });
    }

    // 3. Giải mã token
    try {
        const decoded = jwt.verify(token, config.jwt.secret);
        req.user = decoded; // Lưu thông tin user vào request để Controller dùng
        next(); // Cho phép đi tiếp
    } catch (err) {
        console.log("❌ Lỗi Verify Token:", err.message);
        console.log("👉 Token nhận được:", token);
        console.log("👉 Secret Key đang dùng:", config.jwt.secret);
        return res.status(401).json({ success: false, message: "Token không hợp lệ hoặc đã hết hạn" });
    }
};

module.exports = authMiddleware;