import Joi from 'joi';

const update = Joi.object({
  name: Joi.string()
    .min(2)
    .max(50),

  email: Joi.string()
    .email(),

  password_hash: Joi.string()
    .min(6),
}).min(1);

export default { update };