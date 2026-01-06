const db = require('../config/db.config');

class BlogModel {
    static async findAll({ search, sortBy, sortOrder }) {
        // 👇 SỬA LỖI Ở ĐÂY: u.name -> u.username
        let query = `
            SELECT b.*, u.username as author_name 
            FROM blogs b
            JOIN users u ON b.user_id = u.id
        `;
        
        let params = [];

        if (search) {
            query += " WHERE b.title LIKE ?";
            params.push(`%${search}%`);
        }

        const validSort = ['title', 'created_at', 'id'];
        const finalSort = validSort.includes(sortBy) ? `b.${sortBy}` : 'b.created_at';
        const finalOrder = (sortOrder === 'ASC') ? 'ASC' : 'DESC';

        query += ` ORDER BY ${finalSort} ${finalOrder}`;

        const [rows] = await db.query(query, params);
        return rows;
    }

    static async findById(id) {
        // 👇 SỬA LỖI Ở ĐÂY LUÔN: u.name -> u.username
        const query = `
            SELECT b.*, u.username as author_name 
            FROM blogs b
            JOIN users u ON b.user_id = u.id
            WHERE b.id = ?
        `;
        const [rows] = await db.query(query, [id]);
        return rows[0];
    }

    static async create({ userId, title, content, image }) {
        const [res] = await db.query(
            "INSERT INTO blogs (user_id, title, content, image) VALUES (?,?,?,?)",
            [userId, title, content, image]
        );
        return res.insertId;
    }

    static async update(id, { title, content, image }) {
        let fields = [], params = [];
        if (title) { fields.push("title = ?"); params.push(title); }
        if (content) { fields.push("content = ?"); params.push(content); }
        if (image) { fields.push("image = ?"); params.push(image); }
        
        if (fields.length === 0) return null;
        
        params.push(id);
        const [res] = await db.query(`UPDATE blogs SET ${fields.join(', ')} WHERE id = ?`, params);
        return res;
    }

    static async delete(id) {
        const [res] = await db.query("DELETE FROM blogs WHERE id = ?", [id]);
        return res;
    }
}
module.exports = BlogModel;