const express = require('express');
const cors = require('cors');
const path = require('path');
const config = require('./config/app.config');
const errorHandler = require('./middlewares/error.middleware');

// --- THAY ĐỔI LỚN Ở ĐÂY ---
// Chỉ cần import 1 file index, nó tự hiểu là routes/index.js
const apiRoutes = require('./routes'); 

const app = express();

// --- Middlewares ---
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// --- Routes ---
// Gom tất cả vào prefix '/api'. 
// Nghĩa là mọi đường dẫn đều bắt đầu bằng /api/...
app.use('/api', apiRoutes);

// --- Root Route ---
app.get('/', (req, res) => {
    res.json({ message: '🚀 Server E4-LTM đang chạy chuẩn Senior MVC!' });
});

// --- Error Handler ---
app.use(errorHandler);

// --- Start Server ---
app.listen(config.port, () => {
    console.log(`\n==================================================`);
    console.log(`🚀 SERVER READY: http://localhost:${config.port}`);
    console.log(`--------------------------------------------------`);
    console.log(`👉 API Endpoint: http://localhost:${config.port}/api`);
    console.log(`👉 Health Check: http://localhost:${config.port}/api/health`);
    console.log(`==================================================\n`);
});