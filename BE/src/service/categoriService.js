import db from '../config/db.js';

const getAll = async ({ type }) => {
  const params = [];
  let where = 'WHERE user_id IS NULL';

  if (type) {
    where += ` AND type = $1`;
    params.push(type);
  }

  const result = await db.query(
    `SELECT id, name, type, icon
     FROM categories
     ${where}
     ORDER BY type, name`,
    params
  );

  return result.rows;
};

export default { getAll };