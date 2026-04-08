/* eslint-disable no-console */

// Init the environment variables and server configurations
require('dotenv').config();

// Import the required packages
const Mongoose = require('mongoose');
const config = require('./environment/config');
const app = require('./app');
const userAddedListener = require('./message-bus/recieve/user.added');  // ← Добавьте импорт

console.log('DB URI from config:', config.db.uri);

// Init Database Connection
Mongoose.connect(config.db.uri, {
  useNewUrlParser: true,
  useUnifiedTopology: true
});
Mongoose.connection.on('error', console.error);
Mongoose.connection.on('connected', () => console.log('MongoDB connected successfully'));

// Запускаем RabbitMQ listener ПОСЛЕ подключения к БД
Mongoose.connection.on('connected', async () => {
  await userAddedListener.start();  // ← Запускаем listener
});

// Run the API Server
app.listen(config.port, () => {
  console.log(config.startedMessage);
});