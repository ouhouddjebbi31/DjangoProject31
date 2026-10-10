import { useEffect, useState } from 'react'
import { getMe } from '../services/auth'
import AuthContext from './AuthContext'

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(() => Boolean(localStorage.getItem('access_token')))

  useEffect(() => {
    if (!localStorage.getItem('access_token')) return undefined
    let active = true
    getMe().then((response) => { if (active) setUser(response.data) }).catch(() => localStorage.clear()).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  const logout = () => { localStorage.clear(); setUser(null) }
  return <AuthContext.Provider value={{ user, setUser, loading, logout }}>{children}</AuthContext.Provider>
}
