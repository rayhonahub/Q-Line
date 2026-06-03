import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { authAPI } from "../../api/auth"
import { useAuthStore } from "../../store/authStore"
import toast from "react-hot-toast"
import { Loader2, Eye, EyeOff } from "lucide-react"

export default function LoginPage() {
  const navigate = useNavigate()
  const setAuth  = useAuthStore(s => s.setAuth)

  const [form,    setForm]    = useState({ username: "", password: "" })
  const [loading, setLoading] = useState(false)
  const [show,    setShow]    = useState(false)
  const [error,   setError]   = useState("")

  const f = k => e => {
    setForm({ ...form, [k]: e.target.value })
    setError("")
  }

  const handleSubmit = async e => {
    e.preventDefault()
    if (!form.username || !form.password) {
      setError("Ҳамаи майдонҳоро пур кунед!")
      return
    }
    setLoading(true)
    try {
      const { data } = await authAPI.login(form)
      setAuth(data.user, data.tokens)
      toast.success(`Хуш омадед, ${data.user.username}!`)

      const role = data.user.role
      if (role === "staff") navigate("/staff")
      else navigate("/") 
    } catch (err) {
      console.log("ХАТО:", err.response?.data)
      const msg = err.response?.data?.error || "Username ё парол нодуруст!"
      setError(msg)
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-violet-950 flex">

      {/* ── Чап — Branding ── */}
      <div className="hidden lg:flex w-[45%] flex-col justify-between p-14 relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_left,rgba(99,102,241,0.15),transparent_60%)]" />
        <div className="absolute bottom-0 right-0 w-80 h-80 bg-violet-500/10 rounded-full blur-3xl" />

        <div className="relative flex items-center gap-3">
          <div className="w-10 h-10 bg-white/10 rounded-2xl flex items-center justify-center">
            <span className="text-white font-black text-lg">Q</span>
          </div>
          <span className="text-white font-black text-xl">Q-Line</span>
        </div>

        <div className="relative">
          <h2 className="text-5xl font-black text-white leading-tight mb-6">
            Навбатро<br />
            <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
              ҳушманд
            </span><br />
            идора кун
          </h2>
          <p className="text-slate-400 text-lg mb-10">
            Муштариён вақтро сарфа мекунанд.<br />
            Ташкилотҳо хизматро беҳтар мекунанд.
          </p>
          <div className="grid grid-cols-2 gap-3">
            {[["🏥","Клиникаҳо"],["🏦","Банкҳо"],["🏛️","Идораҳо"],["☕","Тарабхонаҳо"]].map(([icon, label]) => (
              <div key={label} className="flex items-center gap-2.5 bg-white/5 rounded-2xl px-4 py-3">
                <span>{icon}</span>
                <span className="text-slate-300 text-sm font-medium">{label}</span>
              </div>
            ))}
          </div>
        </div>

        <p className="relative text-slate-600 text-xs">© 2026 Q-Line</p>
      </div>

      {/* ── Рост — Form ── */}
      <div className="flex-1 flex items-center justify-center p-6">
        <div className="w-full max-w-sm">
          <div className="bg-white/5 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl">

            {/* Mobile logo */}
            <div className="flex lg:hidden items-center gap-2 mb-8">
              <div className="w-8 h-8 bg-white/10 rounded-xl flex items-center justify-center">
                <span className="text-white font-black">Q</span>
              </div>
              <span className="text-white font-black text-lg">Q-Line</span>
            </div>

            <h1 className="text-2xl font-black text-white mb-1">Хуш омадед</h1>
            <p className="text-slate-400 text-sm mb-8">Маълумотатонро ворид кунед</p>

            <form onSubmit={handleSubmit} className="space-y-4">

              {/* Username */}
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                  Username ё телефон
                </label>
                <input
                  value={form.username}
                  onChange={f("username")}
                  placeholder="ali123 ё +992..."
                  autoComplete="username"
                  className="w-full px-4 py-3.5 rounded-2xl bg-white/10 border-2 border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-400 transition-all text-sm font-medium"
                />
              </div>

              {/* Password */}
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                  Парол
                </label>
                <div className="relative">
                  <input
                    type={show ? "text" : "password"}
                    value={form.password}
                    onChange={f("password")}
                    placeholder="••••••••"
                    autoComplete="current-password"
                    className="w-full px-4 py-3.5 rounded-2xl bg-white/10 border-2 border-white/10 text-white placeholder:text-slate-500 focus:outline-none focus:border-indigo-400 transition-all text-sm font-medium pr-12"
                  />
                  <button
                    type="button"
                    onClick={() => setShow(!show)}
                    className="absolute right-4 top-4 text-slate-400 hover:text-white transition-colors"
                  >
                    {show ? <EyeOff size={16}/> : <Eye size={16}/>}
                  </button>
                </div>
              </div>

              {/* Хато */}
              {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-2xl px-4 py-3">
                  <p className="text-red-400 text-xs font-semibold">⚠️ {error}</p>
                </div>
              )}

              {/* Submit */}
              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-500 to-violet-600 hover:opacity-90 active:scale-95 disabled:opacity-50 text-white font-bold py-4 rounded-2xl transition-all shadow-lg shadow-indigo-900/50 flex items-center justify-center gap-2 mt-2"
              >
                {loading
                  ? <><Loader2 size={16} className="animate-spin"/> Интизор шавед...</>
                  : "Даромадан →"
                }
              </button>
            </form>

            <p className="text-center text-slate-500 text-sm mt-6">
              Аккаунт надоред?{" "}
              <Link to="/register" className="text-indigo-400 font-bold hover:text-indigo-300 transition-colors">
                Қайд шавед
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}