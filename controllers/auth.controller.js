const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const UserModel = require('../models/user.model');
const config = require('../config/app.config');
const asyncHandler = require('../middlewares/asyncio.middleware');

exports.register = asyncHandler(async (req, res) => {
    // 👇 SỬA Ở ĐÂY: Lấy 'username' từ Postman (chứ không phải name)
    const { username, email, password } = req.body;

    // Validate kỹ để tránh lỗi bcrypt undefined
    if (!username || !email || !password) {
        throw { statusCode: 400, message: "Vui lòng nhập đủ: username, email, password" };
    }

    // Kiểm tra trùng email
    const existingUser = await UserModel.findByEmail(email);
    if (existingUser) throw { statusCode: 400, message: "Email đã tồn tại" };

    // Hash pass
    const hashedPassword = await bcrypt.hash(password, 10);

    // Lưu vào DB
    await UserModel.create({ username, email, password: hashedPassword });

    res.status(201).json({ success: true, message: "Đăng ký thành công" });
});

exports.login = asyncHandler(async (req, res) => {
    const { email, password } = req.body;

    if (!email || !password) {
        throw { statusCode: 400, message: "Vui lòng nhập email và password" };
    }

    const user = await UserModel.findByEmail(email);
    if (!user || !(await bcrypt.compare(password, user.password))) {
        throw { statusCode: 401, message: "Sai tài khoản hoặc mật khẩu" };
    }

    const token = jwt.sign({ id: user.id }, config.jwt.secret, { expiresIn: config.jwt.expire });
    const { password: _, ...userInfo } = user;

    res.status(200).json({ success: true, message: "Login thành công", data: { user: userInfo, token } });
});

exports.logout = (req, res) => res.status(200).json({ success: true, message: "Đăng xuất thành công" });