import { create } from "zustand"
import { persist } from "zustand/middleware"

export const useAuthStore = create(
  persist(
    (set, get) => ({
      user:  null,
      token: null,

      setAuth: (user, tokens) => {
        localStorage.setItem("access_token",  tokens.access)
        localStorage.setItem("refresh_token", tokens.refresh)
        set({ user, token: tokens.access })
      },

      logout: () => {
        localStorage.clear()
        set({ user: null, token: null })
      },

      isAuth:       () => !!get().token,
      isCustomer:   () => get().user?.role === "customer",
      isStaff:      () => ["staff","org_admin","super_admin"].includes(get().user?.role),
      isAdmin:      () => ["org_admin","super_admin"].includes(get().user?.role),
      isSuperAdmin: () => get().user?.role === "super_admin",
    }),
    { name: "qline-auth" }
  )
)