const logger = require('winston');
const amqp = require('amqp-ts-async');
const config = require('../../environment/config');
const authController = require('../../controllers/auth.controller');

const exchangeName = 'user.added';
const queueName = '';  // Пустое имя = временная очередь

module.exports = {
  start: async () => {
    try {
      console.log('Connecting to RabbitMQ at:', config.messagebus);

      // 1. Создаём подключение
      const connection = new amqp.Connection(config.messagebus);

      // 2. Ждём готовности подключения
      await connection.completeConfiguration();
      console.log('✅ Connected to RabbitMQ');

      // 3. Объявляем exchange (в amqp-ts-async это делается так)
      const exchange = connection.declareExchange(exchangeName, 'fanout', { durable: true });
      // Не нужно вызывать exchange.declare() - он уже объявлен
      console.log('✅ Exchange declared:', exchangeName);

      // 4. Объявляем очередь (временную, exclusive)
      const queue = await connection.declareQueue(queueName, { exclusive: true });
      console.log('✅ Queue declared:', queue.name);

      // 5. Привязываем очередь к exchange
      await queue.bind(exchange);
      console.log('✅ Queue bound to exchange:', exchangeName);

      // 6. Активируем consumer
      await queue.activateConsumer((msg) => {
        console.log('📨 Message received!');
        authController.add(msg);
      });

      console.log(`✅ Listening for ${exchangeName} events...`);

    } catch (err) {
      console.error('❌ Error setting up RabbitMQ:', err);
      logger.error(`Error: ${err}`);

      // Переподключаемся через 5 секунд
      setTimeout(() => module.exports.start(), 5000);
    }
  },
};