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

// Data Dummy dari User
const DUMMY_TRANSACTIONS = [
  { id: '1', type: 'income', amount: 5000000, category: 'salary', description: 'Gaji Bulanan', date: new Date().toISOString() },
  { id: '2', type: 'expense', amount: 85000, category: 'food', description: 'Makan Bakso', date: new Date().toISOString() },
  { id: '3', type: 'expense', amount: 150000, category: 'transport', description: 'Bensin Mobil', date: new Date(Date.now() - 86400000).toISOString() },
  { id: '4', type: 'expense', amount: 1200000, category: 'bills', description: 'Tagihan Listrik', date: new Date(Date.now() - 172800000).toISOString() },
  { id: '5', type: 'income', amount: 500000, category: 'freelance', description: 'Proyek Desain', date: new Date(Date.now() - 259200000).toISOString() },
];

const categoryLabels = {
  food: "Makanan", transport: "Transportasi", shopping: "Belanja",
  entertainment: "Hiburan", bills: "Tagihan", salary: "Gaji",
  freelance: "Freelance", other: "Lainnya"
};

// 1. Seed User
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

// 2. Seed Kategori secara dinamis berdasarkan data dummy yang ada
const seedCategories = async (userId) => {
  // Ambil kategori unik yang benar-benar dipakai di DUMMY_TRANSACTIONS
  const uniqueCategories = [...new Set(DUMMY_TRANSACTIONS.map(t => t.category))];
  
  const categoryMap = {}; // Untuk menyimpan pasangan { "slug_kategori": "UUID_dari_DB" }

  for (const catKey of uniqueCategories) {
    // Cari nama label aslinya, kalau tidak ada pakai key-nya dengan huruf kapital di awal
    const catName = categoryLabels[catKey] || catKey.charAt(0).toUpperCase() + catKey.slice(1);
    
    // Cari tahu tipenya (income/expense) dari transaksi dummy pertama yang menggunakannya
    const matchedTx = DUMMY_TRANSACTIONS.find(t => t.category === catKey);
    const catType = matchedTx ? matchedTx.type : 'expense';

    const result = await pool.query(
      `
      INSERT INTO categories (id, user_id, name, type)
      VALUES (gen_random_uuid(), $1, $2, $3)
      RETURNING id, name
      `,
      [userId, catName, catType]
    );

    // Simpan UUID yang dihasilkan ke objek map
    categoryMap[catKey] = result.rows[0].id;
  }

  return categoryMap;
};

// 3. Seed Transaksi menggunakan loop dari data dummy
const seedTransactions = async (userId, categoryMap) => {
  for (const tx of DUMMY_TRANSACTIONS) {
    // Ambil UUID kategori yang sesuai dari map hasil langkah ke-2
    const categoryId = categoryMap[tx.category];

    await pool.query(
      `
      INSERT INTO transactions (
        id, user_id, category_id, amount, type, description, date
      )
      VALUES (gen_random_uuid(), $1, $2, $3, $4, $5, $6)
      `,
      [
        userId,
        categoryId,
        tx.amount,
        tx.type,
        tx.description,
        tx.date // Menggunakan date asli dari objek dummy
      ]
    );
  }
};

// Main Execution Function
const runSeed = async () => {
  try {
    console.log("Seeding started...");

    const userId = await seedUsers();
    console.log(`- User created with ID: ${userId}`);

    const categoryMap = await seedCategories(userId);
    console.log("- Categories seeded and mapped successfully.");

    await seedTransactions(userId, categoryMap);
    console.log("- All dummy transactions seeded successfully.");

    console.log("Seeding completed successfully!");
    process.exit(0);
  } catch (err) {
    console.error("Seed error:", err);
    process.exit(1);
  }
};

runSeed();