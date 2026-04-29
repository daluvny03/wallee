import categoriService from '../service/categoriService.js';

const getAll = async (req, res) => {
  try {
    const categories = await categoriService.getAll(req.query);
    res.status(201).json(categories)
  } catch (err) {
    res.status(404).json({ error: err.message });
  }
};

export default { getAll };