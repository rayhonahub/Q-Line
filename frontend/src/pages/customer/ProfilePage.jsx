import { useNavigate } from "react-router-dom"
import { useAuthStore } from "../../store/authStore"
import BottomNav from "../../components/BottomNav"

export default function ProfilePage() {
  const navigate = useNavigate()
  const logout   = useAuthStore(s => s.logout)
  const user     = useAuthStore(s => s.user)

  const roleMap = {
    customer:    { label: "Муштарӣ",  color: "bg-emerald-500/20 text-emerald-300" },
    staff:       { label: "Ходим",    color: "bg-violet-500/20 text-violet-300"   },
    org_admin:   { label: "Admin",    color: "bg-indigo-500/20 text-indigo-300"   },
    super_admin: { label: "Super",    color: "bg-amber-500/20 text-amber-300"     },
  }
  const role = roleMap[user?.role] || roleMap.customer

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-violet-950 pb-24">
      <nav className="sticky top-0 z-40 px-5 py-4 border-b border-white/10 bg-slate-900/80 backdrop-blur-xl">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-xl flex items-center justify-center">
            <span className="text-white font-black text-sm">Q</span>
          </div>
          <span className="text-white font-black">Профил</span>
        </div>
      </nav>

      <div className="max-w-lg mx-auto p-5 mt-4">
        {/* Avatar */}
        <div className="text-center mb-8">
          <div className="w-24 h-24 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-full flex items-center justify-center text-4xl font-black text-white mx-auto mb-4 shadow-xl shadow-indigo-900/50">
            {user?.username?.[0]?.toUpperCase()}
          </div>
          <h1 className="text-2xl font-black text-white">{user?.username}</h1>
          <span className={`inline-block text-xs font-bold px-3 py-1.5 rounded-xl mt-2 ${role.color}`}>
            {role.label}
          </span>
        </div>

        {/* Info */}
        <div className="bg-white/5 border border-white/10 rounded-3xl overflow-hidden mb-4">
          {[
            ["👤", "Username",  user?.username  || "—"],
            ["📧", "Email",     user?.email     || "—"],
            ["📱", "Телефон",   user?.phone     || "—"],
            ["🌐", "Забон",     user?.language  || "tg"],
          ].map(([icon, label, value]) => (
            <div key={label} className="flex items-center justify-between px-5 py-4 border-b border-white/5 last:border-0">
              <div className="flex items-center gap-3">
                <span className="text-lg">{icon}</span>
                <span className="text-slate-400 text-sm font-medium">{label}</span>
              </div>
              <span className="text-white text-sm font-bold">{value}</span>
            </div>
          ))}
        </div>

        {/* Logout */}
        <button
          onClick={() => { logout(); navigate("/login") }}
          className="w-full bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-400 font-bold py-4 rounded-2xl transition-all text-sm"
        >
          🚪 Хориҷ шудан
        </button>
      </div>

      <BottomNav onLogout={() => { logout(); navigate("/login") }} />
    </div>
  )
}