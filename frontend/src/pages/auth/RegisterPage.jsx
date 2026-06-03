import { useState } from "react"
import { useNavigate, Link } from "react-router-dom"
import { authAPI } from "../../api/auth"
import { Loader2, Check } from "lucide-react"
import toast from "react-hot-toast"

const fields = [
  { key: "username",  label: "Username",     placeholder: "ali123",         type: "text"     },
  { key: "email",     label: "Email",         placeholder: "ali@gmail.com",  type: "email"    },
  { key: "phone",     label: "Телефон",       placeholder: "+992 XXX XX XX", type: "tel"      },
  { key: "password",  label: "Парол",         placeholder: "••••••••",       type: "password" },
  { key: "password2", label: "Парол тасдиқ",  placeholder: "••••••••",       type: "password" },
]

export default function RegisterPage() {
  const navigate = useNavigate()

  const [form,    setForm]    = useState({ username:"", email:"", phone:"", password:"", password2:"" })
  const [errors,  setErrors]  = useState({})
  const [loading, setLoading] = useState(false)

  const f = k => e => {
    setForm({ ...form, [k]: e.target.value })
    setErrors({ ...errors, [k]: "" })
  }

  const validate = () => {
    const e = {}
    if (!form.username)                   e.username  = "Username лозим аст"
    if (!form.email)                      e.email     = "Email лозим аст"
    if (!form.phone)                      e.phone     = "Телефон лозим аст"
    if (form.password.length < 8)         e.password  = "Парол ҳадди ақал 8 аломат"
    if (form.password !== form.password2) e.password2 = "Паролҳо мувофиқ нестанд"
    return e
  }

  const handleSubmit = async e => {
    e.preventDefault()
    const errs = validate()
    if (Object.keys(errs).length) { setErrors(errs); return }

    setLoading(true)
    try {
      await authAPI.register({ ...form, language: "tg" })
      toast.success("Қайд муваффақ шуд! Ҳозир кирофтан кунед.")
      navigate("/login")
    } catch (err) {
      console.log("ХАТО:", err.response?.data)
      const data = err.response?.data || {}
      const mapped = {}
      Object.keys(data).forEach(k => {
        mapped[k] = Array.isArray(data[k]) ? data[k][0] : data[k]
      })
      setErrors(mapped)
      toast.error("Маълумотро тасдиқ кунед!")
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
            Қайди нав<br />
            <span className="bg-gradient-to-r from-indigo-400 to-violet-400 bg-clip-text text-transparent">
              осон ва зуд
            </span>
          </h2>
          <p className="text-slate-400 text-lg mb-10">
            Як маротиба қайд шавед —<br />
            ҳама ҷо навбат гиред.
          </p>
          <div className="space-y-3">
            {[
              ["✅", "Навбат аз телефон"],
              ["🔔", "Хабардиҳии Telegram"],
              ["⏱",  "Вақти интизориро кам кунед"],
              ["⭐", "Хизматро баҳо диҳед"],
            ].map(([icon, text]) => (
              <div key={text} className="flex items-center gap-3 text-slate-300 text-sm">
                <span className="w-8 h-8 bg-white/10 rounded-xl flex items-center justify-center">{icon}</span>
                {text}
              </div>
            ))}
          </div>
        </div>

        <p className="relative text-slate-600 text-xs">© 2026 Q-Line</p>
      </div>

      {/* ── Рост — Form ── */}
      <div className="flex-1 flex items-center justify-center p-6 overflow-y-auto">
        <div className="w-full max-w-sm py-8">

          {/* Mobile logo */}
          <div className="flex lg:hidden items-center gap-2 mb-8">
            <div className="w-8 h-8 bg-white/10 rounded-xl flex items-center justify-center">
              <span className="text-white font-black">Q</span>
            </div>
            <span className="text-white font-black text-lg">Q-Line</span>
          </div>

          <div className="bg-white/5 backdrop-blur-2xl border border-white/10 rounded-3xl p-8 shadow-2xl">
            <h1 className="text-2xl font-black text-white mb-1">Қайд шудан</h1>
            <p className="text-slate-400 text-sm mb-8">Маълумотатонро ворид кунед</p>

            <form onSubmit={handleSubmit} className="space-y-4">
              {fields.map(({ key, label, placeholder, type }) => (
                <div key={key}>
                  <label className="block text-xs font-bold text-slate-400 uppercase tracking-widest mb-2">
                    {label}
                  </label>
                  <input
                    type={type}
                    value={form[key]}
                    onChange={f(key)}
                    placeholder={placeholder}
                    className={`w-full px-4 py-3.5 rounded-2xl bg-white/10 border-2 text-white placeholder:text-slate-500 focus:outline-none transition-all text-sm font-medium ${
                      errors[key]
                        ? "border-red-500/50 focus:border-red-400"
                        : "border-white/10 focus:border-indigo-400"
                    }`}
                  />
                  {errors[key] && (
                    <p className="text-red-400 text-xs font-semibold mt-1.5 ml-1">⚠️ {errors[key]}</p>
                  )}
                </div>
              ))}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-indigo-500 to-violet-600 hover:opacity-90 active:scale-95 disabled:opacity-50 text-white font-bold py-4 rounded-2xl transition-all shadow-lg shadow-indigo-900/50 flex items-center justify-center gap-2 mt-2"
              >
                {loading
                  ? <><Loader2 size={16} className="animate-spin"/> Интизор шавед...</>
                  : <><Check size={16}/> Қайд шудан</>
                }
              </button>
            </form>

            <p className="text-center text-slate-500 text-sm mt-6">
              Аккаунт доред?{" "}
              <Link to="/login" className="text-indigo-400 font-bold hover:text-indigo-300 transition-colors">
                Даромадан
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}