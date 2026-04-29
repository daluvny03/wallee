import pg from "pg";
import bcrypt from "bcrypt";
import dotenv from "dotenv";
dotenv.config();

const { Pool } = pg;

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  ssl: process.env.DATABASE_URL?.includes("neon")
    ? { rejectUnauthorized: false }
    : false,
});

const seedTransactions = async (userId, categories) => {
  await pool.query(
    `
    INSERT INTO transactions (
      id, user_id, category_id, amount, type, description, date
    )
    VALUES 
    (
      gen_random_uuid(),
      $1,
      $2,
      50000,
      'expense',
      'Makan siang',
      NOW()
    ),
    (
      gen_random_uuid(),
      $1,
      $3,
      3000000,
      'income',
      'Gaji bulan ini',
      NOW()
    ),
    (
      gen_random_uuid(),
      $1,
      $2,
      20000,
      'expense',
      'Beli kopi',
      NOW()
    )
    `,
    [userId, categories[0], categories[1]]
  );
};

const seedUsers = async () => {
  const hashedPassword = await bcrypt.hash("aza123", 10);

  const result = await pool.query(
    `
    INSERT INTO users (id, name, email, password_hash)
    VALUES (gen_random_uuid(), $1, $2, $3)
    RETURNING id
    `,
    ["zidan", "zidan@mail.com", hashedPassword]
  );

  return result.rows[0].id;
};

const seedCategories = async (userId) => {
  const result = await pool.query(
    `
    INSERT INTO categories (id, user_id, name, type)
    VALUES 
    (gen_random_uuid(), $1, 'Food', 'expense'),
    (gen_random_uuid(), $1, 'Salary', 'income'),
    (gen_random_uuid(), $1, 'Transport', 'expense')
    RETURNING id
    `,
    [userId]
  );

  return result.rows.map((r) => r.id);
};

const runSeed = async () => {
  try {
    console.log("Seeding started...");

    const userId = await seedUsers();
    const categories = await seedCategories(userId);
    await seedTransactions(userId, categories);

    console.log("Seeding completed successfully!");
    process.exit(0);
  } catch (err) {
    console.error("Seed error:", err);
    process.exit(1);
  }
};

runSeed();