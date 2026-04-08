const config = {
  name: 'Article Management Service',
  baseAPIRoute: 'api',
  port: process.env.PORT || 8080,
  messagebus: process.env.MESSAGE_BUS || 'amqp://rabbitmq',
  environment: process.env.ENVIRONMENT || 'dev',
  db: {
    uri: process.env.DB_URI || 'mongodb://mongodb:27017/articles_db',
  },
  services: {
  },
  messageTimeout: 500,
  jwtsecret: 'yoursecretkey',
};

config.startedMessage = `${config.name} is running on port ${config.port}/`;

module.exports = config;