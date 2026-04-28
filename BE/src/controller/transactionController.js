import service from '../service/transactionService.js'

const getAll = async (req, res) => {
  try {
    const result = await service.getAll(req.user.id, req.query);
    res.status(201).json(result);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
};

const getOne = async (req, res) => {
  try {
    const trx = await service.getById(req.params.id, req.user.id);
    if (!trx) return res.status(404).json({ error: 'Transaction not found' });
    return res.status(200).json(trx);
  } catch (err) {
    return res.status(400).json({ error: err.message });
  }
};

const create = async (req, res) => {
  try {
    const trx = await service.create(req.user.id, req.body);
    return res.status(201).json(trx);
  } catch (err) {
    return res.status(400).json({ error: err.message });
  }
};

const update = async (req, res) => {
  try {
    const trx = await service.update(req.params.id, req.user.id, req.body);
    return res.status(200).json(trx);
  } catch (err) {
    const status = err.message === 'Transaction not found' ? 404 : 400;
    return res.status(status).json({ error: err.message });
  }
};

const remove = async (req, res) => {
  try {
    await service.remove(req.params.id, req.user.id);
    return res.status(200).json({ message: 'Transaction deleted' });
  } catch (err) {
    const status = err.message === 'Transaction not found' ? 404 : 400;
    return res.status(status).json({ error: err.message });
  }
};

const getSummary = async (req, res) => {
  try {
    const now   = new Date();
    const month = req.query.month || now.getMonth() + 1;
    const year  = req.query.year  || now.getFullYear();
    const result = await service.getSummary(req.user.id, { month, year });
    return res.status(200).json(result);
  } catch (err) {
    return response.error(res, err.message);
    return res.status(400).json({ error: err.message });
  }
};

export default { getAll, getOne, create, update, remove, getSummary };