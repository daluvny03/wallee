import profileService from "../service/ProfileService.js";

const getProfile = async (req, res) => {
  try {
    const profile = await profileService.getProfile(req.user.id);
    res.status(200).json({
      success: true,
      message: "Data Profil sukses diambil",
      data: profile
    });
  } catch (err) {
    res.status(404).json({
      success: false,
      message: err.message,
      data: null
    });
  }
};

const updateProfile = async (req, res) => {
  try {
    const updated = await profileService.updateProfile(req.user.id, req.body);
    res.status(200).json({
      success: true,
      message: "Data Profil sukses diupdate",
      data: updated
    });
  } catch (err) {
    res.status(404).json({
      success: false,
      message: err.message,
      data: null
    });
  }
};

export default { getProfile, updateProfile };