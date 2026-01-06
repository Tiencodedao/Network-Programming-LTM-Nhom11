const express = require('express');
const router = express.Router();
const BlogController = require('../controllers/blog.controller');
// 👇 Đảm bảo file này tồn tại trong folder utils
const upload = require('../utils/upload.util'); 
// 👇 File này vừa tạo ở Bước 1
const authMiddleware = require('../middlewares/auth.middleware'); 

// Public
router.get('/', BlogController.getAll);
router.get('/:id', BlogController.getById);

// Protected
// 👇 Đổi 'thumbnail' thành 'image' cho chuẩn
router.post('/', authMiddleware, upload.single('image'), BlogController.create);
router.put('/:id', authMiddleware, upload.single('image'), BlogController.update);
router.delete('/:id', authMiddleware, BlogController.delete);

module.exports = router;