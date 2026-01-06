const BlogModel = require('../models/blog.model');
const asyncHandler = require('../middlewares/asyncio.middleware');

exports.getAll = asyncHandler(async (req, res) => {
    const { q, sort, order } = req.query;
    const blogs = await BlogModel.findAll({ search: q, sortBy: sort, sortOrder: order });
    res.status(200).json({ success: true, count: blogs.length, data: blogs });
});

exports.create = asyncHandler(async (req, res) => {
    const { title, content } = req.body;
    const image = req.file ? `/uploads/${req.file.filename}` : null;
    const userId = 1; // Mặc định user ID 1 để test

    if (!title || !content) throw { statusCode: 400, message: "Thiếu dữ liệu" };

    const newId = await BlogModel.create({ userId, title, content, image });

    // 👇 CHỖ NÀY DÙNG 201 (CREATED)
    res.status(201).json({ success: true, message: "Tạo bài viết OK", data: { id: newId, title, image } });
});

exports.update = asyncHandler(async (req, res) => {
    const image = req.file ? `/uploads/${req.file.filename}` : undefined;
    await BlogModel.update(req.params.id, { ...req.body, image });

    // 👇 UPDATE XONG DÙNG 200
    res.status(200).json({ success: true, message: "Update thành công" });
});

exports.delete = asyncHandler(async (req, res) => {
    await BlogModel.delete(req.params.id);

    // 👇 DELETE XONG DÙNG 200
    res.status(200).json({ success: true, message: "Xóa thành công" });
});

exports.getById = asyncHandler(async (req, res) => {
    const blog = await BlogModel.findById(req.params.id);
    if(!blog) throw {statusCode: 404, message: "Không tìm thấy"};
    res.status(200).json({ success: true, data: blog });
});