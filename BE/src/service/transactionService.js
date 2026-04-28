import db from '../config/db.js'

// ─── GET ALL ───────────────────────────────────────────────
const getAll = async (userId, { type, startDate, endDate, page = 1, limit = 20 }) => {
  const conditions = ['t.user_id = $1'];
  const params = [userId];
  let i = 2;

  if (type)      { conditions.push(`t.type = $${i++}`);      params.push(type); }
  if (startDate) { conditions.push(`t.date >= $${i++}`);     params.push(startDate); }
  if (endDate)   { conditions.push(`t.date <= $${i++}`);     params.push(endDate); }

  const where  = conditions.join(' AND ');
  const offset = (Number(page) - 1) * Number(limit);

  const [rows, countResult] = await Promise.all([
    db.query(
      `SELECT
         t.id, t.amount, t.type, t.description, t.date,
         t.created_at, t.updated_at,
         c.id   AS category_id,
         c.name AS category_name,
         c.icon AS category_icon
       FROM transactions t
       LEFT JOIN categories c ON t.category_id = c.id
       WHERE ${where}
       ORDER BY t.date DESC, t.created_at DESC
       LIMIT $${i++} OFFSET $${i++}`,
      [...params, Number(limit), offset]
    ),
    db.query(
      `SELECT COUNT(*) FROM transactions t WHERE ${where}`,
      params
    ),
  ]);

  return {
    transactions: rows.rows,
    pagination: {
      total: parseInt(countResult.rows[0].count),
      page:  Number(page),
      limit: Number(limit),
      totalPages: Math.ceil(countResult.rows[0].count / limit),
    },
  };
};

// ─── GET BY ID ─────────────────────────────────────────────
const getById = async (id, userId) => {
  const result = await db.query(
    `SELECT
       t.id, t.amount, t.type, t.description, t.date,
       t.created_at, t.updated_at,
       c.id   AS category_id,
       c.name AS category_name,
       c.icon AS category_icon
     FROM transactions t
     LEFT JOIN categories c ON t.category_id = c.id
     WHERE t.id = $1 AND t.user_id = $2`,
    [id, userId]
  );

  return result.rows[0] || null;
};

// ─── CREATE ────────────────────────────────────────────────
const create = async (userId, { amount, type, description, date, category_id }) => {
  const result = await db.query(
    `INSERT INTO transactions (user_id, category_id, amount, type, description, date)
     VALUES ($1, $2, $3, $4, $5, $6)
     RETURNING *`,
    [userId, category_id || null, amount, type, description || null, date]
  );

  return result.rows[0];
};

// ─── UPDATE ────────────────────────────────────────────────
const update = async (id, userId, fields) => {
  const allowed = ['amount', 'type', 'description', 'date', 'category_id'];
  const setClauses = [];
  const params = [];
  let i = 1;

  for (const key of allowed) {
    if (fields[key] !== undefined) {
      setClauses.push(`${key} = $${i++}`);
      params.push(fields[key]);
    }
  }

  if (!setClauses.length) throw new Error('No valid fields to update');

  // selalu update updated_at
  setClauses.push(`updated_at = now()`);

  params.push(id, userId); // untuk WHERE

  const result = await db.query(
    `UPDATE transactions
     SET ${setClauses.join(', ')}
     WHERE id = $${i++} AND user_id = $${i++}
     RETURNING *`,
    params
  );

  if (!result.rowCount) throw new Error('Transaction not found');
  return result.rows[0];
};

// ─── DELETE ────────────────────────────────────────────────
const remove = async (id, userId) => {
  const result = await db.query(
    'DELETE FROM transactions WHERE id = $1 AND user_id = $2',
    [id, userId]
  );

  if (!result.rowCount) throw new Error('Transaction not found');
};

// ─── SUMMARY (BONUS) ───────────────────────────────────────
const getSummary = async (userId, { month, year }) => {
  const result = await db.query(
    `SELECT
       type,
       SUM(amount) AS total
     FROM transactions
     WHERE user_id = $1
       AND EXTRACT(MONTH FROM date) = $2
       AND EXTRACT(YEAR  FROM date) = $3
     GROUP BY type`,
    [userId, month, year]
  );

  let totalIncome  = 0;
  let totalExpense = 0;

  for (const row of result.rows) {
    if (row.type === 'income')  totalIncome  = parseFloat(row.total);
    if (row.type === 'expense') totalExpense = parseFloat(row.total);
  }

  return {
    month:        Number(month),
    year:         Number(year),
    totalIncome,
    totalExpense,
    balance:      totalIncome - totalExpense,
  };
};

export default { getAll, getById, create, update, remove, getSummary };