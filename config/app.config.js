require('dotenv').config();

const config = {
  env: process.env.NODE_ENV || 'development',
  port: process.env.PORT || 5000,
  db: {
    host: process.env.DB_HOST || 'localhost',
    port: process.env.DB_PORT || 3306,
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASS || '123456',
    database: process.env.DB_NAME || 'blog_db',
  },
  jwt: {
    secret: process.env.JWT_SECRET,
    expire: process.env.JWT_EXPIRE,
  },
};

module.exports = config;