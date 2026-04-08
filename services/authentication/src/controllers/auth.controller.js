const logger = require('winston');
const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const Auth = require('../models/auth.model');
const config = require('../environment/config');

const authController = {
    authenticate: async (ctx) => {
    try {
      console.log('1. Request received for:', ctx.request.body.emailAddress);
      const user = await Auth.findOne({ emailAddress: ctx.request.body.emailAddress });
      console.log('2. User found:', user ? 'Yes' : 'No');

      if (!user) {
        console.log('3. User not found, throwing 404');
        ctx.throw(404);
      }

      console.log('4. Comparing passwords...');
      const passwordMatch = bcrypt.compareSync(ctx.request.body.password, user.password);
      console.log('5. Password match:', passwordMatch);

      if (!passwordMatch) {
        ctx.body = { auth: false, token: null };
      } else {
        console.log('6. Generating token...');
        const token = jwt.sign({ id: user.emailAddress, role: user.role }, config.jwtsecret, {
          expiresIn: 86400,
        });
        ctx.body = { auth: true, token };
      }
    } catch (err) {
      console.log('ERROR in authenticate:', err.message);
      console.log('Full error:', err);
      ctx.throw(500);
    }
  },

  add: async (message) => {
    let user;
    try {
      user = JSON.parse(message.content.toString());
      const hashedPassword = bcrypt.hashSync(user.password, 8);
      await Auth.create({
        role: user.role,
        emailAddress: user.emailAddress,
        password: hashedPassword,
      });
      logger.info(`user auth record created - ${user.emailAddress}`);
    } catch (err) {
      logger.error(`Error creating auth record for user ${user.emailAddress} : ${err}`);
    }
  },
};

module.exports = authController;
