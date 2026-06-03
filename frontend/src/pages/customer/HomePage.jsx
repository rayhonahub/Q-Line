import { useState, useEffect } from "react"
import { useNavigate } from "react-router-dom"
import { useAuthStore } from "../../store/authStore"
import { orgsAPI } from "../../api/organizations"
import { queuesAPI } from "../../api/queues"
import toast from "react-hot-toast"
import { Loader2, ChevronRight, Users, Clock } from "lucide-react"
import BottomNav from "../../components/BottomNav"

export default function HomePage() {
  const navigate = useNavigate()
  const user     = useAuthStore(s => s.user)
  const logout   = useAuthStore(s => s.logout)

  const [step,          setStep]          = useState(0)
  const [orgs,          setOrgs]          = useState([])
  const [branches,      setBranches]      = useState([])
  const [queues,        setQueues]        = useState([])
  const [ticket,        setTicket]        = useState(null)
  const [activeTickets, setActiveTickets] = useState([])
  const [selected,      setSelected]      = useState({ org: null, branch: null, queue: null })
  const [loading,       setLoading]       = useState(false)

  useEffect(() => {
    loadOrgs()
    loadActiveTickets()
  }, [])

  const loadOrgs = async () => {
    setLoading(true)
    try {
      const { data } = await orgsAPI.getPublic()
      setOrgs(data)
    } catch {
      toast.error("Ташкилотҳо юкланмади!")
    } finally {
      setLoading(false)
    }
  }

  const loadActiveTickets = async () => {
    try {
      const { data } = await queuesAPI.myTickets()
      const all = Array.isArray(data) ? data : data.results || []
      setActiveTickets(all.filter(t => ['waiting', 'called', 'serving'].includes(t.status)))
    } catch {}
  }

  const selectOrg = async (org) => {
    setSelected({ org, branch: null, queue: null })
    setLoading(true)
    try {
      const { data } = await orgsAPI.getBranches(org.id)
      setBranches(data)
      setStep(1)
    } catch {
      toast.error("Shubaho girifta nashud!")
    } finally {
      setLoading(false)
    }
  }

  const selectBranch = async (branch) => {
    setSelected(s => ({ ...s, branch, queue: null }))
    setLoading(true)
    try {
      const { data } = await orgsAPI.getQueues(branch.id)
      setQueues(data)
      setStep(2)
    } catch {
      toast.error("Навбатҳо girifta nashud!")
    } finally {
      setLoading(false)
    }
  }

  const selectQueue = async (queue) => {
    setSelected(s => ({ ...s, queue }))

    if (!user?.telegram_id) {
      const botUsername = import.meta.env.VITE_TELEGRAM_BOT_USERNAME
      const botLink = `https://t.me/${botUsername}?start=queue_${queue.id}`
      setTicket({ needTelegram: true, botLink, queueId: queue.id })
      setStep(3)
      return
    }

    setLoading(true)
    try {
      const { data } = await queuesAPI.createTicket(queue.id)
      setTicket(data.ticket || data)
      setStep(3)
      toast.success("Навбат гирифтед!")
      loadActiveTickets()
    } catch (err) {
      const msg = err.response?.data?.error || "Навбат girifta nashud!"
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  const cancelTicket = async (ticketId) => {
    try {
      await queuesAPI.cancel(ticketId)
      toast.success("Навбат рад шуд!")
      setTicket(null)
      setStep(0)
      setSelected({ org: null, branch: null, queue: null })
      loadActiveTickets()
    } catch {
      toast.error("Хато рӯй дод!")
    }
  }

  const statusConfig = {
    waiting: { label: "⏳ Интизор",       bg: "bg-amber-500/20",  text: "text-amber-300"  },
    called:  { label: "📣 Даъват шуд",    bg: "bg-blue-500/20",   text: "text-blue-300"   },
    serving: { label: "✂️ Хизматрасонӣ", bg: "bg-violet-500/20", text: "text-violet-300" },
  }

  const stepLabels = ["Ташкилот", "Шӯъба", "Навбат"]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-violet-950 pb-24">

      {/* Navbar */}
      <nav className="sticky top-0 z-40 px-5 py-4 flex items-center justify-between border-b border-white/10 bg-slate-900/80 backdrop-blur-xl">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-violet-600 rounded-xl flex items-center justify-center">
            <span className="text-white font-black text-sm">Q</span>
          </div>
          <span className="text-white font-black">Q-Line</span>
        </div>
        <div className="bg-white/10 rounded-xl px-3 py-1.5">
          <span className="text-slate-300 text-xs font-bold">{user?.username}</span>
        </div>
      </nav>

      <div className="max-w-lg mx-auto p-5">

        {/* ── ФАЪОЛ НАВБАТҲО — ҲАР ДОИМ БОЛО ── */}
        {activeTickets.length > 0 && step !== 3 && (
          <div className="mt-4 mb-6 space-y-3">
            <div className="flex items-center justify-between">
              <p className="text-xs font-bold text-indigo-400 uppercase tracking-widest">
                🔴 Фаъол навбатҳои шумо
              </p>
              <button onClick={loadActiveTickets}
                className="text-xs text-slate-400 hover:text-white transition-all">
                🔄 
              </button>
            </div>
            {activeTickets.map(t => {
              const s = statusConfig[t.status] || statusConfig.waiting
              return (
                <div key={t.id} className="bg-white/5 border border-white/10 rounded-2xl p-4">
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-indigo-500/20 border border-indigo-500/30 rounded-2xl flex items-center justify-center font-black text-indigo-300 text-sm">
                        {t.number}
                      </div>
                      <div>
                        <p className="text-white font-bold text-sm">
                          {t.queue_name || `Навбат #${t.queue}`}
                        </p>
                        <p className="text-slate-400 text-xs">{t.branch_name || ""}</p>
                      </div>
                    </div>
                    <span className={`text-xs font-bold px-3 py-1.5 rounded-xl ${s.bg} ${s.text}`}>
                      {s.label}
                    </span>
                  </div>

                  {t.status === 'waiting' && (
                    <div className="grid grid-cols-2 gap-2 mb-2">
                      <div className="bg-white/5 rounded-xl p-2.5 text-center">
                        <p className="text-slate-400 text-xs">Пеш аз шумо</p>
                        <p className="text-white font-black">{Math.max(0, (t.position || 1) - 1)} нафар</p>
                      </div>
                      <div className="bg-white/5 rounded-xl p-2.5 text-center">
                        <p className="text-slate-400 text-xs">Тахминан</p>
                        <p className="text-white font-black">~{t.wait_time || 5} дақ</p>
                      </div>
                    </div>
                  )}

                  {t.status === 'called' && t.window_detail && (
                    <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-2.5 mb-2 text-center">
                      <p className="text-blue-300 text-sm font-bold">
                        🪟 {t.window_detail.name}  ташриф оред!
                      </p>
                    </div>
                  )}

                  {['waiting', 'called'].includes(t.status) && (
                    <button onClick={() => cancelTicket(t.id)}
                      className="w-full text-xs text-red-400 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 py-2 rounded-xl transition-all font-bold">
                      ❌ Рад кардан
                    </button>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* ── STEP 3 ── */}
        {step === 3 && ticket ? (

          ticket.needTelegram ? (
            <div className="mt-4">
              <div className="bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800 rounded-3xl p-8 text-center shadow-2xl relative overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
                <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />
                <div className="relative">
                  <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center text-4xl mx-auto mb-5">✈️</div>
                  <h2 className="text-2xl font-black text-white mb-2">Bo yorii Telegram navbat gired!</h2>
                  <p className="text-blue-200 text-sm mb-6 leading-relaxed">
                    Baroi navbat giriftan va xabarho ba telegram boti mo hamroh shaved
                  </p>
                  <a href={ticket.botLink} target="_blank" rel="noopener noreferrer"
                    className="block w-full bg-white text-blue-700 font-black py-4 rounded-2xl text-base hover:bg-blue-50 transition-all shadow-lg mb-4">
                    ✈️ Ba Telegram guzashtan
                  </a>
                  <p className="text-blue-300 text-xs">Dar bot /start ro paxsh kuned avtomati navbat megired</p>
                </div>
              </div>
              <button onClick={() => { setStep(2); setTicket(null) }}
                className="w-full mt-3 bg-white/5 hover:bg-white/10 border border-white/10 text-slate-400 hover:text-white font-bold py-4 rounded-2xl transition-all text-sm">
                ← Ba qafo
              </button>
            </div>

          ) : (
            <div className="mt-4 space-y-3">
              <div className="bg-gradient-to-br from-indigo-600 via-indigo-700 to-violet-800 rounded-3xl p-8 text-center shadow-2xl shadow-indigo-900/50 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-40 h-40 bg-white/5 rounded-full -translate-y-1/2 translate-x-1/2" />
                <div className="absolute bottom-0 left-0 w-32 h-32 bg-white/5 rounded-full translate-y-1/2 -translate-x-1/2" />
                <div className="relative">
                  <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center text-3xl mx-auto mb-4">🎉</div>
                  <p className="text-indigo-200 text-xs font-bold uppercase tracking-widest mb-2">Рақами навбати шумо</p>
                  <p className="text-8xl font-black text-white tracking-tight mb-6">{ticket.number}</p>
                  <div className="grid grid-cols-2 gap-3 mb-4">
                    <div className="bg-white/10 rounded-2xl p-4">
                      <div className="flex items-center justify-center gap-1.5 mb-1">
                        <Users size={14} className="text-indigo-200"/>
                        <p className="text-xs text-indigo-200 font-medium">Пеш аз шумо</p>
                      </div>
                      <p className="text-2xl font-black text-white">
                        {Math.max(0, (ticket.position || 1) - 1)} нафар
                      </p>
                    </div>
                    <div className="bg-white/10 rounded-2xl p-4">
                      <div className="flex items-center justify-center gap-1.5 mb-1">
                        <Clock size={14} className="text-indigo-200"/>
                        <p className="text-xs text-indigo-200 font-medium">Тахминан</p>
                      </div>
                      <p className="text-2xl font-black text-white">~{ticket.wait_time || 5} дақ</p>
                    </div>
                  </div>
                  <div className="bg-white/10 rounded-2xl px-4 py-2.5 mb-3">
                    <p className="text-indigo-200 text-xs font-medium">
                      🏢 {selected.org?.name} • {selected.branch?.name}
                    </p>
                  </div>
                  <p className="text-indigo-300 text-xs">🔔 Bo vositai teelgram xabar megired</p>
                </div>
              </div>

              <button onClick={() => cancelTicket(ticket.id)}
                className="w-full bg-white/5 hover:bg-red-500/20 border border-white/10 hover:border-red-500/30 text-slate-400 hover:text-red-400 font-bold py-4 rounded-2xl transition-all text-sm">
                ❌ Навбат рад кардан
              </button>
              <button onClick={() => { setStep(0); setTicket(null); setSelected({ org: null, branch: null, queue: null }) }}
                className="w-full bg-white/5 hover:bg-white/10 border border-white/10 text-slate-400 hover:text-white font-bold py-4 rounded-2xl transition-all text-sm">
                + Навбати нав гирифтан
              </button>
            </div>
          )

        ) : (
          <>
            <div className="mt-6 mb-6">
              <h1 className="text-2xl font-black text-white">Салом, {user?.username}! 👋</h1>
              <p className="text-slate-400 text-sm mt-1">Навбат гиред — вақтро сарфа накунед</p>
            </div>

            {step > 0 && (
              <div className="flex items-center gap-1.5 mb-5 overflow-x-auto pb-1">
                {stepLabels.map((s, i) => (
                  <div key={i} className="flex items-center gap-1.5 shrink-0">
                    <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl transition-all text-xs font-bold ${
                      i < step   ? "bg-indigo-600/30 text-indigo-300" :
                      i === step ? "bg-indigo-500 text-white" :
                                   "bg-white/5 text-slate-500"
                    }`}>
                      <span className={`w-4 h-4 rounded-full flex items-center justify-center text-xs font-black ${
                        i < step   ? "bg-indigo-400 text-white" :
                        i === step ? "bg-white text-indigo-600" :
                                     "bg-white/10 text-slate-500"
                      }`}>
                        {i < step ? "✓" : i + 1}
                      </span>
                      {s}
                    </div>
                    {i < 2 && <ChevronRight size={12} className="text-slate-600"/>}
                  </div>
                ))}
              </div>
            )}

            {step > 0 && (
              <div className="flex items-center gap-2 mb-4 flex-wrap">
                {selected.org && (
                  <button onClick={() => { setStep(0); setSelected({ org: null, branch: null, queue: null }) }}
                    className="text-xs bg-white/10 hover:bg-white/20 text-slate-300 px-3 py-1.5 rounded-xl transition-all font-medium">
                    ← {selected.org.name}
                  </button>
                )}
                {selected.branch && step > 1 && (
                  <button onClick={() => { setStep(1); setSelected(s => ({ ...s, branch: null, queue: null })) }}
                    className="text-xs bg-white/10 hover:bg-white/20 text-slate-300 px-3 py-1.5 rounded-xl transition-all font-medium">
                    ← {selected.branch.name}
                  </button>
                )}
              </div>
            )}

            {loading && (
              <div className="flex items-center justify-center py-20">
                <Loader2 size={36} className="animate-spin text-indigo-400"/>
              </div>
            )}

            {!loading && step === 0 && (
              <div className="space-y-3">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Ташкилотро интихоб кунед</p>
                {orgs.length === 0 ? (
                  <div className="text-center py-20">
                    <p className="text-5xl mb-3">🏢</p>
                    <p className="font-bold text-slate-400">Ташкилот мавҷуд нест</p>
                  </div>
                ) : orgs.map(org => (
                  <button key={org.id} onClick={() => selectOrg(org)}
                    className="w-full bg-white/5 hover:bg-white/10 border border-white/10 hover:border-indigo-400/50 rounded-2xl px-5 py-4 text-left transition-all group flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-11 h-11 bg-gradient-to-br from-indigo-400 to-violet-600 rounded-2xl flex items-center justify-center text-white font-black text-lg shadow-lg">
                        {org.name[0]}
                      </div>
                      <div>
                        <p className="font-bold text-white group-hover:text-indigo-300 transition-colors">{org.name}</p>
                        <p className="text-xs text-slate-400 mt-0.5 capitalize">{org.plan} план</p>
                      </div>
                    </div>
                    <ChevronRight size={18} className="text-slate-500 group-hover:text-indigo-400 transition-colors"/>
                  </button>
                ))}
              </div>
            )}

            {!loading && step === 1 && (
              <div className="space-y-3">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Шӯъбаро интихоб кунед</p>
                {branches.length === 0 ? (
                  <div className="text-center py-20">
                    <p className="text-5xl mb-3">🏬</p>
                    <p className="font-bold text-slate-400">Шӯъба мавҷуд нест</p>
                  </div>
                ) : branches.map(branch => (
                  <button key={branch.id} onClick={() => selectBranch(branch)}
                    className="w-full bg-white/5 hover:bg-white/10 border border-white/10 hover:border-indigo-400/50 rounded-2xl px-5 py-4 text-left transition-all group flex items-center justify-between">
                    <div>
                      <p className="font-bold text-white group-hover:text-indigo-300 transition-colors">{branch.name}</p>
                      {branch.address && <p className="text-xs text-slate-400 mt-0.5">📍 {branch.address}</p>}
                    </div>
                    <ChevronRight size={18} className="text-slate-500 group-hover:text-indigo-400 transition-colors"/>
                  </button>
                ))}
              </div>
            )}

            {!loading && step === 2 && (
              <div className="space-y-3">
                <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Навбатро интихоб кунед</p>
                {queues.length === 0 ? (
                  <div className="text-center py-20">
                    <p className="text-5xl mb-3">📋</p>
                    <p className="font-bold text-slate-400">Навбат мавҷуд нест</p>
                  </div>
                ) : queues.map(queue => (
                  <button key={queue.id} onClick={() => selectQueue(queue)}
                    className="w-full bg-white/5 hover:bg-white/10 border border-white/10 hover:border-indigo-400/50 rounded-2xl px-5 py-5 text-left transition-all group flex items-center justify-between">
                    <div>
                      <p className="font-bold text-white group-hover:text-indigo-300 transition-colors text-lg">{queue.name}</p>
                      <div className="flex items-center gap-3 mt-2">
                        <span className="flex items-center gap-1 text-xs text-slate-400">
                          <Users size={12}/>{queue.waiting_count || 0} нафар интизор
                        </span>
                        <span className="flex items-center gap-1 text-xs text-slate-400">
                          <Clock size={12}/>~{(queue.waiting_count || 0) * 5} дақ
                        </span>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-2xl font-black text-indigo-400">{queue.prefix}</span>
                      <ChevronRight size={18} className="text-slate-500 group-hover:text-indigo-400 transition-colors"/>
                    </div>
                  </button>
                ))}
              </div>
            )}
          </>
        )}
      </div>

      <BottomNav onLogout={() => { logout(); navigate("/login") }} />
    </div>
  )
}