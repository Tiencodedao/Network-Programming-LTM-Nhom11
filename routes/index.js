const express = require('express')
const authRoutes = require('./auth.route')
const blogRoutes = require('./blog.route')

const router = express.Router()

router.use('/auth', authRoutes)
router.use('/blogs', blogRoutes)

module.exports = router