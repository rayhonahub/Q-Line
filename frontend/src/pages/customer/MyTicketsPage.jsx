import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuthStore } from "../../store/authStore"
import { queuesAPI } from "../../api/queues"
import { Loader2 } from "lucide-react"
import BottomNav from "../../components/BottomNav"
import toast from "react-hot-toast"

export default function MyTicketsPage() {
  const navigate = useNavigate()
  const logout   = useAuthStore(s => s.logout)
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(false)
  const [ratingMap, setRatingMap] = useState({})

  useEffect(() => {
    load()
  }, [])

  const load = async () => {
    setLoading(true)
    try {
      const { data } = await queuesAPI.myTickets()
      const all = Array.isArray(data) ? data : data.results || []
      setTickets(all)
    } catch (err) {
      toast.error("Навбатҳо юкланмади!")
    } finally {
      setLoading(false)
    }
  }

  const handleCancel = async (id) => {
    try {
      await queuesAPI.cancel(id)
      toast.success("Навбат рад шуд!")
      load()
    } catch {
      toast.error("Хато рӯй дод!")
    }
  }

  const handleRate = async (ticketId, stars) => {
    setRatingMap(r => ({ ...r, [ticketId]: stars }))
    try {
      await queuesAPI.rate(ticketId, stars)
      toast.success("Баҳо берилди! ⭐")
      load()
    } catch {
      toast.error("Баҳо берилмади!")
      setRatingMap(r => ({ ...r, [ticketId]: null }))
    }
  }

  const statusConfig = {
    waiting:   { label: "⏳ Интизор",       bg: "bg-amber-500/20",   text: "text-amber-300",   border: "border-amber-500/30"   },
    called:    { label: "📣 Даъват шуд",    bg: "bg-blue-500/20",    text: "text-blue-300",    border: "border-blue-500/30"    },
    serving:   { label: "✂️ Хизматрасонӣ", bg: "bg-violet-500/20",  text: "text-violet-300",  border: "border-violet-500/30"  },
    completed: { label: "✅ Тамом",         bg: "bg-emerald-500/20", text: "text-emerald-300", border: "border-emerald-500/30" },
    cancelled: { label: "❌ Рад шуд",       bg: "bg-red-500/20",     text: "text-red-300",     border: "border-red-500/30"     },
    no_show:   { label: "🚫 Наомад",        bg: "bg-slate-500/20",   text: "text-slate-300",   border: "border-slate-500/30"   },
  }

  const activeTickets    = tickets.filter(t => ['waiting', 'called', 'serving'].includes(t.status))
  const completedTickets = tickets.filter(t => ['completed', 'cancelled', 'no_show'].includes(t.status))

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-violet-950 pb-24">

      {/* Navbar */}
      <nav className="sticky top-0 z-40 px-5 py-4 flex items-center justify-between border-b border-white/10 bg-slate-900/80 backdrop-blur-xl">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-xl flex items-center justify-center">
            <span className="text-white font-black text-sm">Q</span>
          </div>
          <span className="text-white font-black">Навбатҳои ман</span>
        </div>
        <button onClick={load}
          className="text-xs text-indigo-400 bg-indigo-500/10 px-3 py-1.5 rounded-xl font-bold hover:bg-indigo-500/20 transition-all">
          🔄 Янгилаш
        </button>
      </nav>

      <div className="max-w-lg mx-auto p-5">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <Loader2 size={36} className="animate-spin text-indigo-400"/>
          </div>
        ) : tickets.length === 0 ? (
          <div className="text-center py-24">
            <p className="text-5xl mb-4">🎫</p>
            <p className="text-white font-bold text-lg">Навбат мавҷуд нест</p>
            <p className="text-slate-400 text-sm mt-2">Асосӣ саҳифада навбат гиред</p>
            <button onClick={() => navigate("/")}
              className="mt-6 bg-indigo-600 hover:bg-indigo-700 text-white font-bold px-6 py-3 rounded-2xl transition-all text-sm">
              Навбат гирифтан →
            </button>
          </div>
        ) : (
          <div className="space-y-6 mt-4">

            {/* ── Фаъол навбатҳо ── */}
            {activeTickets.length > 0 && (
              <div>
                <p className="text-xs font-bold text-indigo-400 uppercase tracking-widest mb-3">
                  🔴 Фаъол — {activeTickets.length} та
                </p>
                <div className="space-y-3">
                  {activeTickets.map(ticket => {
                    const s = statusConfig[ticket.status] || statusConfig.waiting
                    return (
                      <div key={ticket.id}
                        className={`bg-white/5 border ${s.border} rounded-2xl p-5`}>
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className="w-14 h-14 bg-indigo-500/20 border border-indigo-500/30 rounded-2xl flex items-center justify-center font-black text-indigo-300 text-lg">
                              {ticket.number}
                            </div>
                            <div>
                              <p className="text-white font-bold text-sm">
                                {ticket.queue_name || `Навбат #${ticket.queue}`}
                              </p>
                              <p className="text-slate-400 text-xs mt-0.5">
                                📍 {ticket.branch_name || ""}
                              </p>
                              <p className="text-slate-500 text-xs">
                                {new Date(ticket.created_at).toLocaleString("ru")}
                              </p>
                            </div>
                          </div>
                          <span className={`text-xs font-bold px-3 py-1.5 rounded-xl ${s.bg} ${s.text}`}>
                            {s.label}
                          </span>
                        </div>

                        {/* Позиция */}
                        {ticket.status === 'waiting' && (
                          <div className="grid grid-cols-2 gap-2 mb-3">
                            <div className="bg-white/5 rounded-xl p-3 text-center">
                              <p className="text-slate-400 text-xs">Пеш аз шумо</p>
                              <p className="text-white font-black text-lg">
                                {Math.max(0, (ticket.position || 1) - 1)} нафар
                              </p>
                            </div>
                            <div className="bg-white/5 rounded-xl p-3 text-center">
                              <p className="text-slate-400 text-xs">Тахминан</p>
                              <p className="text-white font-black text-lg">
                                ~{ticket.wait_time || 5} дақ
                              </p>
                            </div>
                          </div>
                        )}

                        {/* Даъват шуд — дарча */}
                        {ticket.status === 'called' && ticket.window_detail && (
                          <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-3 mb-3 text-center">
                            <p className="text-blue-300 text-sm font-bold">
                              🪟 {ticket.window_detail.name} дарчасига ташриф оваред!
                            </p>
                          </div>
                        )}

                        {/* Рад кардан */}
                        {['waiting', 'called'].includes(ticket.status) && (
                          <button onClick={() => handleCancel(ticket.id)}
                            className="w-full text-xs text-red-400 hover:text-red-300 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 py-2.5 rounded-xl transition-all font-bold">
                            ❌ Навбат рад кардан
                          </button>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

            {/* ── Тарих + Рейтинг ── */}
            {completedTickets.length > 0 && (
              <div>
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
                  📋 Тарих — {completedTickets.length} та
                </p>
                <div className="space-y-3">
                  {completedTickets.map(ticket => {
                    const s = statusConfig[ticket.status] || statusConfig.completed
                    const currentRating = ratingMap[ticket.id] || ticket.rating
                    return (
                      <div key={ticket.id}
                        className="bg-white/5 border border-white/10 rounded-2xl p-5">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 bg-white/10 rounded-2xl flex items-center justify-center font-black text-slate-300 text-sm">
                              {ticket.number}
                            </div>
                            <div>
                              <p className="text-white font-bold text-sm">
                                {ticket.queue_name || `Навбат #${ticket.queue}`}
                              </p>
                              <p className="text-slate-500 text-xs">
                                {new Date(ticket.created_at).toLocaleString("ru")}
                              </p>
                            </div>
                          </div>
                          <span className={`text-xs font-bold px-3 py-1.5 rounded-xl ${s.bg} ${s.text}`}>
                            {s.label}
                          </span>
                        </div>

                        {/* ── Рейтинг — фақат completed учун ── */}
                        {ticket.status === 'completed' && (
                          <div className="mt-2 pt-3 border-t border-white/10">
                            <p className="text-xs text-slate-400 mb-2">
                              {currentRating ? "⭐ Баҳои шумо:" : "Хизматга баҳо беринг:"}
                            </p>
                            <div className="flex gap-2">
                              {[1, 2, 3, 4, 5].map(star => (
                                <button
                                  key={star}
                                  onClick={() => !ticket.rating && handleRate(ticket.id, star)}
                                  disabled={!!ticket.rating}
                                  className={`text-2xl transition-all hover:scale-125 ${
                                    star <= (currentRating || 0)
                                      ? "text-amber-400"
                                      : "text-slate-600 hover:text-amber-300"
                                  } ${ticket.rating ? "cursor-default" : "cursor-pointer"}`}
                                >
                                  ⭐
                                </button>
                              ))}
                              {currentRating && (
                                <span className="text-amber-300 text-sm font-bold ml-2 self-center">
                                  {currentRating}/5
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                    )
                  })}
                </div>
              </div>
            )}

          </div>
        )}
      </div>

      <BottomNav onLogout={() => { logout(); navigate("/login") }} />
    </div>
  )
}