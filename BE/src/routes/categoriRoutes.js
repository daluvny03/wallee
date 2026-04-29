import express from 'express';
const router = express.Router();
import controller from '../controller/categoriController.js';
import auth from '../middleware/authMiddleware.js';

router.use(auth);

router.get('/', controller.getAll);

export default router;