import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles, Trash2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

// --- DATA DARI CLAUDE ---
const QUICK_CHIPS = [
  "Rangkum pengeluaran bulan ini",
  "Kategori apa yang paling boros?",
  "Berikan tips hemat untuk saya",
  "Bandingkan bulan ini vs bulan lalu",
];

function getDemoReply(msg) {
  const m = msg.toLowerCase();
  if (m.includes("pengeluaran"))
    return "Total pengeluaranmu bulan ini adalah **Rp 2.384.500**, turun 23% dibanding bulan lalu. Kategori terbesar adalah Makanan (35%) dan Transport (22%). 📊";
  if (m.includes("boros") || m.includes("kategori"))
    return "Kategori paling boros bulan ini adalah 🍔 **Makanan & Minuman** dengan Rp 845.000. Kamu bisa coba meal prep untuk menghemat hingga 30% di kategori ini!";
  if (m.includes("tips") || m.includes("hemat"))
    return "Berikut 3 tips hemat berdasarkan data keuanganmu:\n\n1. **Kurangi langganan streaming** — kamu punya 3 aktif sekaligus\n2. **Batasi makan di luar** max 8x/bulan\n3. **Sisihkan 20% gaji** di hari pertama menerima gaji 💡";
  if (m.includes("banding") || m.includes("lalu"))
    return "Perbandingan bulan ini vs bulan lalu:\n\n📈 **Pemasukan:** Rp 8.500.000 (sama)\n📉 **Pengeluaran:** Rp 2.384.500 vs Rp 3.100.000\n💰 **Selisih:** hemat Rp 715.500 bulan ini! 🎉";
  return "Terima kasih atas pertanyaanmu! Berdasarkan data keuanganmu, saya sedang menganalisis. Untuk hasil terbaik, coba hubungkan akun bankmu ke Wallee 😊";
}

export default function Chat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Halo! Saya adalah AI Financial Assistant Wallee. 👋\nAda yang bisa saya bantu soal keuanganmu hari ini?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollRef = useRef(null);

  // Auto scroll
  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  const handleSend = async (textToSend = input) => {
    const trimmed = textToSend.trim();
    if (!trimmed || isLoading) return;

    // Tambah pesan user
    const userMessage = { role: 'user', content: trimmed };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulasi delay AI (Alur Claude)
    await new Promise((r) => setTimeout(r, 1200));
    const reply = getDemoReply(trimmed);

    setMessages(prev => [...prev, { role: 'assistant', content: reply }]);
    setIsLoading(false);
  };

  const clearChat = () => {
    setMessages([{
      role: 'assistant',
      content: 'Halo! Saya adalah AI Financial Assistant Wallee. 👋\nAda yang bisa saya bantu soal keuanganmu hari ini?'
    }]);
  };

  return (
    <div className="flex flex-col h-screen lg:h-screen bg-slate-50">
      {/* Header - Style Base44 */}
      <div className="p-4 md:px-8 md:py-5 border-b border-gray-200 bg-blue-50/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="flex items-center justify-between max-w-3xl mx-auto w-full">
          <div className="flex items-center gap-3">
            <div className="bg-gradient-to-br from-[#3975E6] to-[#9E4CC6] p-2 rounded-xl">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h1 className="font-semibold">AI Financial Assistant</h1>
              <div className="flex items-center gap-1.5">
                <p className="text-xs text-muted-foreground">Powered By AI • Selalu siap membantu</p>
              </div>
            </div>
          </div>
          
          <button
            onClick={clearChat}
            className="flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium text-muted-foreground hover:bg-destructive/10 hover:text-destructive transition-colors cursor-pointer"
          >
            <Trash2 className="w-4 h-4" />
            <span className="hidden sm:inline">Hapus Riwayat</span>
          </button>
        </div>
      </div>

      {/* Messages Area - Style Base44 */}
      <div className="flex-1 overflow-y-auto p-4 md:px-8 space-y-6 max-w-3xl mx-auto w-full">
        <AnimatePresence>
          {messages.map((msg, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className={`flex gap-3 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              {msg.role === 'assistant' && (
                <div className="bg-gradient-to-br from-[#3975E6] to-[#9E4CC6] w-8 h-8 rounded-xl flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
                  <Bot className="w-4 h-4 text-white" />
                </div>
              )}
              <div className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 shadow-sm ${
                msg.role === 'user'
                  ? 'bg-gradient-to-br from-[#3975E6] to-[#9E4CC6] text-white rounded-tr-none'
                  : 'bg-card border border-gray-200/50 rounded-tl-none text-card-foreground'
              }`}>
                {msg.role === 'user' ? (
                  <p className="text-sm leading-relaxed">{msg.content}</p>
                ) : (
                  <div className="text-sm prose prose-sm max-w-none dark:prose-invert">
                    <ReactMarkdown
                      components={{
                        p: ({ children }) => <p className="my-1 leading-relaxed">{children}</p>,
                        ul: ({ children }) => <ul className="my-1 ml-4 list-disc">{children}</ul>,
                        li: ({ children }) => <li className="my-0.5">{children}</li>,
                        strong: ({ children }) => <strong className="font-bold text-primary">{children}</strong>,
                      }}
                    >
                      {msg.content}
                    </ReactMarkdown>
                  </div>
                )}
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-xl bg-muted flex items-center justify-center shrink-0 mt-0.5 border border-border/50">
                  <User className="w-4 h-4 text-muted-foreground" />
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {/* Quick Chips dari Claude */}
        {messages.length === 1 && !isLoading && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            className="flex flex-wrap gap-2 ml-11"
          >
            {QUICK_CHIPS.map((chip) => (
              <button
                key={chip}
                onClick={() => handleSend(chip)}
                className="px-3 py-1.5 rounded-full border border-border bg-background text-xs font-medium text-muted-foreground hover:border-primary hover:text-primary hover:bg-primary/5 transition-all"
              >
                {chip}
              </button>
            ))}
          </motion.div>
        )}

        {isLoading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-3">
            <div className="bg-gradient-to-br from-[#3975E6] to-[#9E4CC6] w-8 h-8 rounded-xl flex items-center justify-center shrink-0 shadow-sm">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-card border border-gray-200/50 rounded-2xl rounded-tl-none px-4 py-3 shadow-sm">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="w-4 h-4 animate-spin text-primary" />
                <span>Wallee sedang berpikir...</span>
              </div>
            </div>
          </motion.div>
        )}
        <div ref={scrollRef} className="h-4" />
      </div>

      {/* Input Area - Style Base44 */}
      <div className="p-4 md:px-8 md:py-5 border-t border-gray-200 bg-blue-50/50 backdrop-blur-sm mb-16 lg:mb-0">
        <form
          onSubmit={(e) => { e.preventDefault(); handleSend(); }}
          className="max-w-3xl mx-auto flex gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend();
              }
            }}
            placeholder="Tanya tentang keuangan Anda..."
            className="flex-1 h-12 px-4 bg-gray-100 border border-gray-300/50 rounded-xl outline-none focus:ring-2 focus:ring-primary/20 disabled:opacity-50 transition-all"
            disabled={isLoading}
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="bg-gradient-to-br from-[#3975E6] to-[#9E4CC6] p-3 rounded-xl text-white disabled:opacity-50 transition-all hover:shadow-lg hover:shadow-primary/25 active:scale-95"
          >
            <Send className="w-5 h-5" />
          </button>
        </form>
      </div>
    </div>
  );
}