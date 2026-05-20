import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, BarChart3, Calendar } from 'lucide-react';
import Card from '../components/ui/card';
import SelectFields from '../components/ui/select';
import { getTransactions } from '../services/transactionService';

const DUMMY_TRANSACTIONS = [
  { id: '1', type: 'income',  amount: 5000000, category: 'salary',        date: '2026-05-13' },
  { id: '2', type: 'expense', amount: 150000,  category: 'food',          date: '2026-05-01' },
  { id: '3', type: 'expense', amount: 200000,  category: 'transport',     date: '2026-05-03' },
  { id: '4', type: 'expense', amount: 450000,  category: 'shopping',      date: '2026-05-04' },
  { id: '5', type: 'expense', amount: 80000,   category: 'food',          date: '2026-05-05' },
  { id: '6', type: 'income',  amount: 1200000, category: 'freelance',     date: '2026-05-06' },
  { id: '7', type: 'expense', amount: 300000,  category: 'bills',         date: '2026-05-07' },
  { id: '8', type: 'expense', amount: 120000,  category: 'entertainment', date: '2026-05-08' },
];

const categoryLabels = {
  food: "Makanan", transport: "Transport", shopping: "Belanja",
  entertainment: "Hiburan", bills: "Tagihan", health: "Kesehatan",
  salary: "Gaji", freelance: "Freelance", other: "Lainnya",
};

const COLORS = ['#3975E6', '#9E4CC6', '#34D399', '#F59E0B', '#EF4444', '#6366F1', '#EC4899', '#14B8A6'];

function formatCurrency(val) {
  return new Intl.NumberFormat('id-ID', {
    style: 'currency', currency: 'IDR', maximumFractionDigits: 0,
  }).format(val);
}

// ── Page ──────────────────────────────────────────────────────
export default function Analytics() {
  const [period, setPeriod]         = useState('month');
  const [transactions, setTransactions] = useState([]);
  const fetchTransactions = async () => {
      try {
        const data = await getTransactions();
        console.log("API response for transactions:", data.data.transactions);
        setTimeout(() => {
        setTransactions(data.data.transactions);
      }, 0);
      } catch (error) {
        console.log(error);
      }
    };
  
    useEffect(() => {
      fetchTransactions();
    }, []);
  const now = new Date();
  const filtered = transactions.filter(tx => {
    if (!tx.date) return false;
    const d = new Date(tx.date);
    if (period === 'week') {
      const weekAgo = new Date(now);
      weekAgo.setDate(weekAgo.getDate() - 7);
      return d >= weekAgo;
    }
    if (period === 'month') {
      return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
    }
    if (period === 'year') {
      return d.getFullYear() === now.getFullYear();
    }
    return true;
  });
  const totalIncome  = filtered.filter(t => t.type === 'income').reduce((s, t) => s + parseFloat(t.amount), 0);
  const totalExpense = filtered.filter(t => t.type === 'expense').reduce((s, t) => s + parseFloat(t.amount), 0);

  const categoryData = Object.entries(
    filtered.filter(t => t.type === 'expense').reduce((acc, t) => {
      const CategoryName = t?.category_name || "Lainnya";
      acc[CategoryName] = (acc[CategoryName] || 0) + parseFloat(t.amount);
      return acc;
    }, {})
  )
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value);

  const dailyData = filtered
    .reduce((acc, t) => {
      const day = new Date(t.date).getDate().toString();
      const existing = acc.find(i => i.date === day);
      if (existing) {
        if (t.type === 'income') existing.income  += t.amount;
        else                     existing.expense += t.amount;
      } else {
        acc.push({
          date:    day,
          income:  t.type === 'income'  ? t.amount : 0,
          expense: t.type === 'expense' ? t.amount : 0,
        });
      }
      return acc;
    }, [])
    .sort((a, b) => parseInt(a.date) - parseInt(b.date));

  return (
    <div className="p-4 md:p-8 max-w-3xl mx-auto space-y-6 min-h-screen">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-gray-900">Analitik</h1>
          <p className="text-sm text-gray-400">Pantau kesehatan keuangan Anda</p>
        </div>

        <div className="relative">
            <SelectFields 
              value={period} 
              onChange={(e) => setPeriod(e.target.value)}
              className="appearance-none w-30 text-xs"
            >
            <option value="week">Minggu Ini</option>
            <option value="month">Bulan Ini</option>
            <option value="year">Tahun Ini</option>
          </SelectFields>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 gap-4">
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
          <Card className="p-5 border border-gray-100 overflow-hidden relative">
            <div className="absolute top-0 right-0 p-3">
              <TrendingUp className="w-8 h-8 text-emerald-600" />
            </div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-emerald-500" />
              <span className="text-xs text-gray-400 font-semibold uppercase tracking-wider">Pemasukan</span>
            </div>
            <p className="text-xl md:text-2xl font-bold text-emerald-600">{formatCurrency(totalIncome)}</p>
          </Card>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <Card className="p-5 border border-gray-100 overflow-hidden relative">
            <div className="absolute top-0 right-0 p-3">
              <TrendingDown className="w-8 h-8 text-red-400" />
            </div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-red-500" />
              <span className="text-xs text-gray-400 font-semibold uppercase tracking-wider">Pengeluaran</span>
            </div>
            <p className="text-xl md:text-2xl font-bold text-gray-900">{formatCurrency(totalExpense)}</p>
          </Card>
        </motion.div>
      </div>

      {/* Bar Chart */}
      <Card className="p-6 border border-gray-100">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-sm font-bold flex items-center gap-2 text-gray-800">
            <BarChart3 className="w-4 h-4 text-blue-500" />
            Tren Transaksi Harian
          </h3>
        </div>
        <div className="w-full h-60">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={dailyData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
              <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 11, fill: '#94a3b8' }} axisLine={false} tickLine={false} tickFormatter={(v) => v >= 1000 ? `${v / 1000}k` : v} />
              <Tooltip
                cursor={{ fill: '#f8fafc' }}
                formatter={(value) => [formatCurrency(value), ""]}
                contentStyle={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '12px', fontSize: '12px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
              />
              <Bar dataKey="income"  fill="#10b981" radius={[4, 4, 0, 0]} maxBarSize={15} />
              <Bar dataKey="expense" fill="#3975E6" radius={[4, 4, 0, 0]} maxBarSize={15} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="flex justify-center gap-4 mt-4">
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
            <span className="text-[10px] text-gray-400">Pemasukan</span>
          </div>
          <div className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded-full bg-[#3975E6]" />
            <span className="text-[10px] text-gray-400">Pengeluaran</span>
          </div>
        </div>
      </Card>

      {/* Pie Chart */}
      <Card className="p-6 border border-gray-100">
        <h3 className="text-sm font-bold mb-6 text-gray-800">Distribusi Pengeluaran</h3>
        <div className="flex flex-col md:flex-row items-center gap-8">
          <div className="w-full max-w-[200px] h-[200px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={categoryData} cx="50%" cy="50%" innerRadius={60} outerRadius={85} paddingAngle={5} dataKey="value">
                  {categoryData.map((_, idx) => (
                    <Cell key={idx} fill={COLORS[idx % COLORS.length]} stroke="none" />
                  ))}
                </Pie>
                <Tooltip formatter={(value) => formatCurrency(value)} contentStyle={{ borderRadius: '12px', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="flex-1 w-full grid grid-cols-1 gap-3">
            {categoryData.slice(0, 5).map((cat, i) => (
              <div key={cat.name} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-4 h-4 rounded-full" style={{ backgroundColor: COLORS[i % COLORS.length] }} />
                  <div>
                    <p className="text-sm font-medium text-gray-700">{cat.name}</p>
                    <p className="text-[10px] text-gray-400">Kategori Pengeluaran</p>
                  </div>
                </div>
                <span className="text-sm font-bold text-gray-800">{formatCurrency(cat.value)}</span>
              </div>
            ))}
          </div>
        </div>
      </Card>

    </div>
  );
}