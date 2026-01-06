const mysql = require('mysql2');
// QUAN TRỌNG: Gọi đúng file app.config.js
const config = require('./app.config'); 

const pool = mysql.createPool({
    ...config.db, // Lấy cấu hình db từ app.config
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
});

const promisePool = pool.promise();

promisePool.getConnection()
    .then(conn => {
        console.log(`✅ [Database] Connected to MySQL: ${config.db.database}`);
        conn.release();
    })
    .catch(err => {
        console.error('❌ [Database] Connection Failed:', err.message);
    });

module.exports = promisePool;