import { createContext, useContext, useEffect, useState } from 'react'
import { getMe } from '../services/auth'

const AuthContext = createContext(null)
export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  useEffect(() => { if (localStorage.getItem('access_token')) getMe().then((r) => setUser(r.data)).catch(() => localStorage.clear()).finally(() => setLoading(false)); else setLoading(false) }, [])
  const logout = () => { localStorage.clear(); setUser(null) }
  return <AuthContext.Provider value={{ user, setUser, loading, logout }}>{children}</AuthContext.Provider>
}
export const useAuth = () => useContext(AuthContext)
