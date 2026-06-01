import auth from "../middleware/authMiddleware.js";
import express from "express";
import { forecastingController } from "../controller/forecastController.js";

const router = express.Router();
router.use(auth);
router.get("/", forecastingController);

export default router;