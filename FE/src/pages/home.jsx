import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, ChevronRight } from 'lucide-react';
import { LineChart, Sparkles, PieChart } from 'lucide-react';
import { Star } from 'lucide-react';



import Header from '../components/layout/header';
import Footer from '../components/layout/footer';

export function HomeSection() {
  return (
    <div id="home" className="flex flex-col justify-center bg-white w-full min-h-screen pt-20 pb-24">

      <section className="px-6 md:px-12 lg:px-24 max-w-7xl mx-auto w-full">
        {/* Typography */}
        <h1 className="text-5xl md:text-7xl lg:text-[5.5rem] font-bold text-black mb-8 tracking-tight leading-[1.1] font-serif">
          Smart Money<br className="hidden md:block" />
          <span className="bg-gradient-to-br from-blue-500 to-purple-500 text-transparent bg-clip-text">Happy life</span>
        </h1>

        <p className="text-slate-500 text-lg md:text-xl mb-12 leading-relaxed max-w-2xl font-medium">
          Wallee membantu kamu memahami, merencanakan, dan mengoptimalkan pengeluaran dengan lebih cerdas menggunakan teknologi AI.
        </p>

        {/* Action Buttons */}
        <div className="flex items-center space-x-8 mb-24">
          <Link to="/register">
            <button className="flex items-center gap-2 bg-[#e3e9e8] text-[#1f2729] font-bold px-7 py-3.5 rounded-full hover:bg-white transition-all hover:shadow-lg">
              Mulai Gratis <ArrowRight size={20} strokeWidth={2.5} />
            </button>
          </Link>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Stat 1 */}
          <div className="bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl p-8">
            <h3 className="text-4xl font-bold text-white mb-3 font-serif tracking-tight">1 dari 3</h3>
            <p className="text-white text-sm leading-relaxed font-medium">
              orang Indonesia tidak punya tabungan darurat
            </p>
          </div>

          {/* Stat 2 */}
          <div className="bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl p-8">
            <h3 className="text-4xl font-bold text-white mb-3 font-serif tracking-tight">68%</h3>
            <p className="text-white text-sm leading-relaxed font-medium">
              keluarga tidak pernah merencanakan keuangan
            </p>
          </div>

          {/* Stat 3 */}
          <div className="bg-gradient-to-br from-blue-500 to-purple-500 rounded-2xl p-8">
            <h3 className="text-4xl font-bold text-white mb-3 font-serif tracking-tight">Rp 0</h3>
            <p className="text-white text-sm leading-relaxed font-medium">
              yang disisihkan oleh rata-rata pekerja muda
            </p>
          </div>
        </div>
      </section>

    </div>
  );
}

export function Feature() {
  return (
    <section id="feature" className="text-center py-16 px-4 w-full">
      <h2 className="text-3xl font-bold text-slate-900 mb-12">Kenapa Memilih Kami?</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
        {/* Feature 1 */}
        <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm hover:shadow-md transition-shadow flex flex-col items-center">
          <div className="text-blue-500 mb-6 w-16 h-16 flex items-center justify-center">
            <LineChart size={48} strokeWidth={1.5} />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">Tracking Keuangan</h3>
          <p className="text-gray-500 text-sm leading-relaxed">
            Catat pemasukan dan pengeluaran harian dengan mudah dan terstruktur.
          </p>
        </div>

        {/* Feature 2 */}
        <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm hover:shadow-md transition-shadow flex flex-col items-center">
          <div className="text-blue-500 mb-6 w-16 h-16 flex items-center justify-center">
            <Sparkles size={48} strokeWidth={1.5} />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">Analisis AI</h3>
          <p className="text-gray-500 text-sm leading-relaxed">
            Dapatkan insight otomatis tentang pola pengeluaranmu dan rekomendasi yang lebih bijak.
          </p>
        </div>

        {/* Feature 3 */}
        <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm hover:shadow-md transition-shadow flex flex-col items-center">
          <div className="text-blue-500 mb-6 w-16 h-16 flex items-center justify-center">
            <PieChart size={48} strokeWidth={1.5} />
          </div>
          <h3 className="text-xl font-bold text-slate-900 mb-3">Laporan Otomatis</h3>
          <p className="text-gray-500 text-sm leading-relaxed">
            Lihat laporan keuangan dalam bentuk grafik yang mudah dipahami kapan saja.
          </p>
        </div> 
      </div>
    </section>
  );
}

export function Testimoni() {
    return (
        <section className="text-center py-16 px-4 w-full">
            <h2 className="text-3xl font-bold text-slate-900 mb-4">Apa Kata Mereka?</h2>
            <p className="text-gray-500 mb-12 max-w-xl mx-auto">
                Kendalikan keuangan Anda dengan Wallee. Lacak pengeluaran dan menabung lebih cerdas dalam satu aplikasi praktis.
            </p>

            <div className="flex flex-col md:flex-row gap-6 justify-center items-center max-w-5xl mx-auto">
                {/* Card 1 */}
                <div className="bg-gray-50/80 rounded-2xl p-6 w-full md:w-96 text-left border border-gray-100">
                    <div className="w-10 h-10 rounded-full overflow-hidden mb-4">
                        <img src="https://i.pravatar.cc/150?img=11" alt="User" className="w-full h-full object-cover" />
                    </div>
                    <div className="flex text-yellow-400 mb-3">
                        {[...Array(5)].map((_, i) => (
                            <Star key={i} size={16} fill="currentColor" className="mr-1" />
                        ))}
                    </div>
                    <p className="text-slate-900 font-semibold leading-snug">
                        Wallee otomatis mengatur pengeluaran saya dengan sempurna.
                    </p>
                </div>

                {/* Card 2 */}
                <div className="bg-gray-50/80 rounded-2xl p-6 w-full md:w-96 text-left border border-gray-100">
                    <div className="w-10 h-10 rounded-full overflow-hidden mb-4">
                        <img src="https://i.pravatar.cc/150?img=5" alt="User" className="w-full h-full object-cover" />
                    </div>
                    <div className="flex text-yellow-400 mb-3">
                        {[...Array(5)].map((_, i) => (
                            <Star key={i} size={16} fill="currentColor" className="mr-1" />
                        ))}
                    </div>
                    <p className="text-slate-900 font-semibold leading-snug">
                        Saya hanya perlu memotret setelah makan bisnis dan pengeluaran langsung tercatat.
                    </p>
                </div>
            </div>
        </section>
    );
}

export default function Home() {
  return (
    <>
      <Header />
      <div className="w-full min-h-screen bg-slate-50 overflow-x-hidden font-sans">
        <HomeSection />
        <Feature />
        <Testimoni />
      </div>
      <Footer />
    </>
  );
}