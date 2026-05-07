import authService from "../service/authService.js";

const register = async (req, res) => {
  try {
    const user = await authService.register(req.body);
    res.status(200).json({
      success: true,
      message: "Data Pengguna sukses dibuat",
      data: user
    });
  } catch (err) {
    res.status(400).json({ 
      success: false,
      message: err.message,
      data: null
     });
  }
};

const login = async (req, res) => {
  try {
    const data = await authService.login(req.body);
    res.status(200).json({
      success: true,
      message: "Login Berhasil",
      data: data
    });
  } catch (err) {
    res.status(400).json({ 
      success: false,
      message: err.message,
      data: null
     });
  }
};

export default {
  register,
  login,
};