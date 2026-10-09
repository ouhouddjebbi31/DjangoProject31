import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar'
import { AuthProvider } from './context/AuthContext'
import Home from './pages/Home'
import Explore from './pages/Explore'
import Details from './pages/Details'
import { Login, Register } from './pages/AuthPages'
import { Library, ForYou, Profile } from './pages/PrivatePages'
import NotFound from './pages/NotFound'
import './theme.css'

function App() {
  return <AuthProvider><BrowserRouter><Navbar /><Routes><Route path="/" element={<Home />} /><Route path="/books" element={<Explore />} /><Route path="/books/:id" element={<Details />} /><Route path="/login" element={<Login />} /><Route path="/register" element={<Register />} /><Route path="/library" element={<Library />} /><Route path="/for-you" element={<ForYou />} /><Route path="/profile" element={<Profile />} /><Route path="*" element={<NotFound />} /></Routes></BrowserRouter></AuthProvider>
}

export default App
