import { useState } from "react";
import { motion } from "framer-motion";
import { toast, Toaster } from "sonner";
import { Lock, Key } from "lucide-react";
import Card from "../components/ui/card";
import ButtonGrad from "../components/ui/buttongrad";
import InputFields from "../components/ui/input";
import { changePassword } from "../services/user_service";

export default function ChangePassword() {
  const [form, setForm] = useState({
    currentPassword: "",
    newPassword: "",
    confirmPassword: "",
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const validate = () => {
    const err = {};
    if (!form.currentPassword) err.currentPassword = "Password saat ini wajib diisi";
    if (!form.newPassword) err.newPassword = "Password baru wajib diisi";
    else if (form.newPassword.length < 6) err.newPassword = "Password baru minimal 6 karakter";
    if (!form.confirmPassword) err.confirmPassword = "Konfirmasi password wajib diisi";
    else if (form.newPassword !== form.confirmPassword) err.confirmPassword = "Password tidak cocok";
    return err;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const validationErrors = validate();
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length) return;

    setLoading(true);
    try {
      await changePassword({
        currentPassword: form.currentPassword,
        newPassword: form.newPassword,
      });
      toast.success("Password berhasil diubah");
      setForm({ currentPassword: "", newPassword: "", confirmPassword: "" });
    } catch (err) {
      toast.error(err.response?.data?.message || err.message || "Gagal mengubah password");
    } finally {
      setLoading(false);
    }
  };

  const setField = (field) => (e) => {
    setForm((prev) => ({ ...prev, [field]: e.target.value }));
    setErrors((prev) => ({ ...prev, [field]: "" }));
  };

  return (
    <div className="p-4 md:p-8 max-w-2xl mx-auto space-y-6 min-h-screen bg-slate-50">
      <Toaster position="top-right" richColors />

      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-2xl font-bold tracking-tight text-[hsl(225,20%,12%)]">Ganti Password</h1>
        <p className="text-sm text-[hsl(220,10%,46%)] mt-1">Perbarui kata sandi akun Anda dengan aman.</p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="bg-gradient-to-br from-[#3975E6] to-[#9E4CC6] p-2.5 rounded-xl">
              <Lock className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-semibold text-black">Keamanan Akun</h2>
              <p className="text-xs text-[hsl(220,10%,46%)]">Ubah kata sandi Anda secara berkala.</p>
            </div>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-1.5">
              <label className="text-sm font-medium px-1">Password Saat Ini</label>
              <InputFields
                type="password"
                value={form.currentPassword}
                onChange={setField("currentPassword")}
                placeholder="Masukkan password saat ini"
              />
              {errors.currentPassword && (
                <p className="text-xs text-red-500">{errors.currentPassword}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium px-1">Password Baru</label>
              <InputFields
                type="password"
                value={form.newPassword}
                onChange={setField("newPassword")}
                placeholder="Masukkan password baru"
              />
              {errors.newPassword && (
                <p className="text-xs text-red-500">{errors.newPassword}</p>
              )}
            </div>

            <div className="space-y-1.5">
              <label className="text-sm font-medium px-1">Konfirmasi Password Baru</label>
              <InputFields
                type="password"
                value={form.confirmPassword}
                onChange={setField("confirmPassword")}
                placeholder="Ulangi password baru"
              />
              {errors.confirmPassword && (
                <p className="text-xs text-red-500">{errors.confirmPassword}</p>
              )}
            </div>

            <ButtonGrad
              type="submit"
              disabled={loading}
              className="w-full h-12 rounded-xl text-white font-semibold text-sm shadow-lg shadow-primary/20 hover:opacity-90 active:scale-[0.98] transition-all"
            >
              {loading ? "Menyimpan..." : "Simpan Password"}
            </ButtonGrad>
          </form>
        </Card>
      </motion.div>
    </div>
  );
}
