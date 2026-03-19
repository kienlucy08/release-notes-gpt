require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');

const clickupRoutes = require('./routes/clickup');
const generateRoutes = require('./routes/generate');

const app = express();
const PORT = process.env.PORT || 3001;

app.use(
  cors({
    origin: process.env.CORS_ORIGIN || 'http://localhost:5173',
    methods: ['GET', 'POST'],
  })
);
app.use(express.json());

// API Routes
app.use('/api', clickupRoutes);
app.use('/api', generateRoutes);

// In production, serve React build
if (process.env.NODE_ENV === 'production') {
  app.use(express.static(path.join(__dirname, '../client/dist')));
  app.get('*', (req, res) => {
    res.sendFile(path.join(__dirname, '../client/dist/index.html'));
  });
}

app.listen(PORT, () => {
  console.log(`API server running on port ${PORT}`);
});
