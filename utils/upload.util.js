const multer = require('multer');
const path = require('path');
const fs = require('fs');

// 1. Tự động tạo thư mục 'uploads' nếu chưa có
const uploadDir = 'uploads';
if (!fs.existsSync(uploadDir)) {
    fs.mkdirSync(uploadDir);
}

// 2. Cấu hình nơi lưu và tên file
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, uploadDir); // Lưu vào thư mục uploads
    },
    filename: (req, file, cb) => {
        // Đặt tên file: image-thời_gian-số_ngẫu_nhiên.jpg
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

// 3. Chỉ cho phép upload ảnh
const fileFilter = (req, file, cb) => {
    if (file.mimetype.startsWith('image/')) {
        cb(null, true);
    } else {
        cb(new Error('Chỉ chấp nhận file ảnh!'), false);
    }
};

// 4. Khởi tạo Multer
const upload = multer({ 
    storage: storage,
    fileFilter: fileFilter,
    limits: { fileSize: 5 * 1024 * 1024 } // Giới hạn 5MB
});

module.exports = upload;