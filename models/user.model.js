const db = require('../config/db.config');

class UserModel {
    static async create({ username, email, password }) {
        // 👇 QUAN TRỌNG: Cột trong DB là 'username', không phải 'name'
        const [result] = await db.query(
            "INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
            [username, email, password]
        );
        return result.insertId;
    }

    static async findByEmail(email) {
        const [rows] = await db.query("SELECT * FROM users WHERE email = ?", [email]);
        return rows[0];
    }

    static async findById(id) {
        const [rows] = await db.query("SELECT * FROM users WHERE id = ?", [id]);
        return rows[0];
    }
}

module.exports = UserModel;