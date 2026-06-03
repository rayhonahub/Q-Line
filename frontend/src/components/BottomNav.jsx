import { useNavigate, useLocation } from "react-router-dom"
import { Home, Ticket, User, LogOut } from "lucide-react"

export default function BottomNav({ onLogout }) {
  const navigate = useNavigate()
  const location = useLocation()

  const tabs = [
    { icon: Home,   label: "Асосӣ",     path: "/"           },
    { icon: Ticket, label: "Навбатҳоям",path: "/my-tickets" },
    { icon: User,   label: "Профил",    path: "/profile"    },
  ]

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50">
      <div className="bg-slate-900/95 backdrop-blur-xl border-t border-white/10 px-4 py-3">
        <div className="max-w-lg mx-auto flex items-center justify-around">
          {tabs.map(({ icon: Icon, label, path }) => {
            const active = location.pathname === path
            return (
              <button key={path} onClick={() => navigate(path)}
                className={`flex flex-col items-center gap-1 px-4 py-1 rounded-2xl transition-all ${
                  active ? "text-indigo-400" : "text-slate-500 hover:text-slate-300"
                }`}>
                <Icon size={22}/>
                <span className="text-xs font-bold">{label}</span>
              </button>
            )
          })}
          <button onClick={onLogout}
            className="flex flex-col items-center gap-1 px-4 py-1 text-slate-500 hover:text-red-400 transition-all">
            <LogOut size={22}/>
            <span className="text-xs font-bold">Хориҷ</span>
          </button>
        </div>
      </div>
    </div>
  )
}