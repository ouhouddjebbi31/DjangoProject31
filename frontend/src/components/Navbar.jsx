import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout } = useAuth()
  return <nav className="navbar navbar-expand-lg site-nav"><div className="container"><Link className="navbar-brand" to="/">BookWise <span>AI</span></Link><div className="d-flex gap-3 align-items-center"><Link to="/books">Explore</Link>{user && <><Link to="/library">Library</Link><Link to="/for-you">For you</Link><Link to="/profile">Profile</Link></>}{user ? <button className="btn btn-sm btn-outline-light" onClick={logout}>Log out</button> : <Link className="btn btn-sm btn-burgundy" to="/login">Log in</Link>}</div></div></nav>
}
