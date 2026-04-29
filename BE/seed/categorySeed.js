import dotenv from 'dotenv';
dotenv.config();
import db from '../src/config/db.js';

const categories = [
  // ─── EXPENSE ───────────────────────────────
  { name: 'Makanan & Minuman', type: 'expense', icon: '🍔' },
  { name: 'Transportasi',      type: 'expense', icon: '🚗' },
  { name: 'Belanja',           type: 'expense', icon: '🛍️' },
  { name: 'Kesehatan',         type: 'expense', icon: '💊' },
  { name: 'Pendidikan',        type: 'expense', icon: '📚' },
  { name: 'Hiburan',           type: 'expense', icon: '🎮' },
  { name: 'Tagihan & Utilitas',type: 'expense', icon: '🧾' },
  { name: 'Perawatan Diri',    type: 'expense', icon: '💆' },
  { name: 'Rumah Tangga',      type: 'expense', icon: '🏠' },
  { name: 'Pakaian',           type: 'expense', icon: '👕' },
  { name: 'Olahraga',          type: 'expense', icon: '🏋️' },
  { name: 'Sosial',            type: 'expense', icon: '🎉' },
  { name: 'Lainnya',           type: 'expense', icon: '📦' },

  // ─── INCOME ────────────────────────────────
  { name: 'Gaji',              type: 'income',  icon: '💰' },
  { name: 'Freelance',         type: 'income',  icon: '💻' },
  { name: 'Bisnis',            type: 'income',  icon: '🏢' },
  { name: 'Investasi',         type: 'income',  icon: '📈' },
  { name: 'Hadiah',            type: 'income',  icon: '🎁' },
  { name: 'Lainnya',           type: 'income',  icon: '📦' },
];

const seed = async () => {
  console.log('Seeding categories...');

  // Cek apakah sudah pernah di-seed (hindari duplikat)
  const existing = await db.query(
    'SELECT COUNT(*) FROM categories WHERE user_id IS NULL'
  );

  if (parseInt(existing.rows[0].count) > 0) {
    console.log('Default categories sudah ada, seed dibatalkan.');
    process.exit(0);
  }

  // Insert semua kategori
  for (const cat of categories) {
    await db.query(
      `INSERT INTO categories (name, type, icon, is_default)
       VALUES ($1, $2, $3, true)`,
      [cat.name, cat.type, cat.icon]
    );
  }

  console.log(`${categories.length} categories berhasil di-seed!`);
  process.exit(0);
};

seed().catch((err) => {
  console.error('Seed gagal:', err.message);
  process.exit(1);
});