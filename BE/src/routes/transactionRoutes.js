import express from 'express';
import controller from '../controller/transactionController.js';
import auth from '../middleware/authMiddleware.js';

const router = express.Router();
// semua route butuh token
router.use(auth);

router.get('/',           controller.getAll);
router.get('/summary',    controller.getSummary);   // ⚠️ harus sebelum /:id
router.get('/:id',        controller.getOne);
router.post('/',          controller.create);
router.put('/:id',        controller.update);
router.delete('/:id',     controller.remove);

export default router;