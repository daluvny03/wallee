import service from '../service/transactionService.js'

const getAll = async (req, res) => {
  try {
    const result = await service.getAll(req.user.id, req.query);
    res.status(200).json({
      success: true,
      message: "Data Transaksi sukses diambil",
      data: result
    });
  } catch (err) {
    res.status(400).json({
      success: false,
      message: err.message,
      data: null
    });
  }
};

const getOne = async (req, res) => {
  try {
    const trx = await service.getById(req.params.id, req.user.id);
    if (!trx) return res.status(404).json({
      success: false,
      message: 'Data Transaksi tidak ditemukan',
      data: null
    });
    return res.status(200).json({
      success: true,
      message: "Data Transaksi sukses diambil",
      data: trx
    });
  } catch (err) {
    return res.status(400).json({
      success: false,
      message: err.message,
      data: null
    });
  }
};

const create = async (req, res) => {
  try {
    const trx = await service.create(req.user.id, req.body);
    return res.status(201).json({
      success: true,
      message: "Data Transaksi sukses dibuat",
      data: trx
    });
  } catch (err) {
    return res.status(400).json({
      success: false,
      message: err.message,
      data: null
    });
  }
};

const update = async (req, res) => {
  try {
    const trx = await service.update(req.params.id, req.user.id, req.body);
    return res.status(200).json({
      success: true,
      message: "Data Transaksi sukses diupdate",
      data: trx
    });
  } catch (err) {
    const status = err.message === 'Data Transaksi tidak ditemukan' ? 404 : 400;
    return res.status(status).json({
      success: false,
      message: err.message,
      data: null
    });
  }
};

const remove = async (req, res) => {
  try {
    await service.remove(req.params.id, req.user.id);
    return res.status(200).json({
      success: true,
      message: 'Data Transaksi sukses dihapus',
      data: null
    });
  } catch (err) {
    const status = err.message === 'Data Transaksi tidak ditemukan' ? 404 : 400;
    return res.status(status).json({
      success: false,
      message: err.message,
      data: null
    });
  }
};

const getSummary = async (req, res) => {
  try {
    const now   = new Date();
    const month = req.query.month || now.getMonth() + 1;
    const year  = req.query.year  || now.getFullYear();
    const result = await service.getSummary(req.user.id, { month, year });
    return res.status(200).json({
      success: true,
      message: "Ringkasan Transaksi sukses diambil",
      data: result
    });
  } catch (err) {
    return res.status(400).json({
      success: false,
      message: err.message,
      data: null
    });
  }
};

export default { getAll, getOne, create, update, remove, getSummary };