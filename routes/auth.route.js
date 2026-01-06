const router = require('express').Router();
const C = require('../controllers/auth.controller');
// Chú ý: Import controller phải chuẩn
router.post('/register', C.register);
router.post('/login', C.login);
router.post('/logout', C.logout);
module.exports = router;