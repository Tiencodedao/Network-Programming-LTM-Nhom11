const errorHandler = (err, req, res, next) => {
  console.error(err)
  
  const status = err.status || 500
  const message = err.message || 'Internal Server Error'
  
  res.status(status).json({
    success: false,
    status,
    message,
    ...(process.env.NODE_ENV === 'development' && { error: err })
  })
}

module.exports = errorHandler