import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom"
import { Toaster } from "react-hot-toast"
import { useAuthStore } from "./store/authStore"
import LoginPage    from "./pages/auth/LoginPage"
import RegisterPage from "./pages/auth/RegisterPage"
import HomePage     from "./pages/customer/HomePage"
import MyTicketsPage from "./pages/customer/MyTicketsPage"
import ProfilePage  from "./pages/customer/ProfilePage"

function Private({ children, roles }) {
  const user   = useAuthStore(s => s.user)
  const isAuth = useAuthStore(s => s.isAuth)
  if (!isAuth()) return <Navigate to="/login" replace />
  if (roles && !roles.includes(user?.role)) return <Navigate to="/" replace />
  return children
}

function StaffHome() {
  const user     = useAuthStore(s => s.user)
  const logout   = useAuthStore(s => s.logout)
  const navigate = useNavigate()
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="bg-white rounded-3xl p-10 shadow-sm border border-slate-100 text-center max-w-sm w-full">
        <div className="w-16 h-16 bg-violet-100 rounded-full flex items-center justify-center text-3xl mx-auto mb-4">🧑‍💼</div>
        <h1 className="text-xl font-black text-slate-800 mb-1">Staff панел</h1>
        <p className="text-slate-400 text-sm mb-2">{user?.username}</p>
        <span className="text-xs bg-violet-100 text-violet-600 font-bold px-3 py-1 rounded-full">{user?.role}</span>
        <button onClick={() => { logout(); navigate("/login") }}
          className="w-full mt-6 bg-red-50 hover:bg-red-100 text-red-500 font-bold py-3 rounded-2xl transition-all text-sm">
          Хориҷ шудан
        </button>
      </div>
    </div>
  )
}

function AdminHome() {
  const user     = useAuthStore(s => s.user)
  const logout   = useAuthStore(s => s.logout)
  const navigate = useNavigate()
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center">
      <div className="bg-white rounded-3xl p-10 shadow-sm border border-slate-100 text-center max-w-sm w-full">
        <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center text-3xl mx-auto mb-4">⚙️</div>
        <h1 className="text-xl font-black text-slate-800 mb-1">Admin панел</h1>
        <p className="text-slate-400 text-sm mb-2">{user?.username}</p>
        <span className="text-xs bg-emerald-100 text-emerald-600 font-bold px-3 py-1 rounded-full">{user?.role}</span>
        <button onClick={() => { logout(); navigate("/login") }}
          className="w-full mt-6 bg-red-50 hover:bg-red-100 text-red-500 font-bold py-3 rounded-2xl transition-all text-sm">
          Хориҷ шудан
        </button>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Toaster position="top-right" toastOptions={{
        style: { borderRadius: "16px", fontSize: "14px", fontWeight: 600 }
      }}/>
      <Routes>
        <Route path="/login"    element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route path="/" element={
          <Private roles={["customer","org_admin","super_admin","staff"]}>
            <HomePage />
          </Private>
        }/>
        <Route path="/my-tickets" element={
          <Private roles={["customer","org_admin","super_admin","staff"]}>
            <MyTicketsPage />
          </Private>
        }/>
        <Route path="/profile" element={
          <Private roles={["customer","org_admin","super_admin","staff"]}>
            <ProfilePage />
          </Private>
        }/>
        <Route path="/staff" element={
          <Private roles={["staff","org_admin","super_admin"]}>
            <StaffHome />
          </Private>
        }/>
        <Route path="/admin" element={
          <Private roles={["org_admin","super_admin"]}>
            <AdminHome />
          </Private>
        }/>
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  )
}



