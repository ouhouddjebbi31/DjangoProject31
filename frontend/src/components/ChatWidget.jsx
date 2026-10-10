import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { sendChatMessage } from '../services/chat'

export default function ChatWidget() {
  const { user } = useAuth()
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([])
  const [sending, setSending] = useState(false)
  const [error, setError] = useState('')
  const endRef = useRef(null)

  useEffect(() => {
    const handleQuestion = (event) => { setInput(event.detail); setOpen(true); setError('') }
    window.addEventListener('bookwise:chat-question', handleQuestion)
    return () => window.removeEventListener('bookwise:chat-question', handleQuestion)
  }, [])
  useEffect(() => { endRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [messages, sending])
  if (!user) return null

  const submit = async (event) => {
    event?.preventDefault()
    const message = input.trim()
    if (!message || sending) return
    const history = messages.slice(-6).map(({ role, content }) => ({ role, content }))
    setMessages((current) => [...current, { role: 'user', content: message }])
    setInput(''); setError(''); setSending(true)
    try {
      const response = await sendChatMessage(message, history)
      setMessages((current) => [...current, { role: 'assistant', content: response.data.reply, sources: response.data.sources }])
    } catch (requestError) {
      setError(requestError.response?.data?.error || 'The assistant is unavailable right now.')
    } finally { setSending(false) }
  }

  return <>
    <button className="chat-launcher" onClick={() => setOpen(!open)} aria-label="Open BookWise Assistant">{open ? '×' : '✦'}</button>
    {open && <section className="chat-panel" aria-label="BookWise Assistant"><header><div><p className="eyebrow">BookWise Assistant</p><strong>Your catalog librarian</strong></div><button className="chat-clear" onClick={() => { setMessages([]); setError('') }}>Clear chat</button></header><div className="chat-messages">{messages.length === 0 && <p className="chat-empty">Ask about a book, author, genre, or what to read next.</p>}{messages.map((item, index) => <div className={`chat-message ${item.role}`} key={`${item.role}-${index}`}><p>{item.content}</p>{item.sources?.length > 0 && <div className="chat-sources">{item.sources.map((source) => <Link key={source.id} to={`/books/${source.id}`} onClick={() => setOpen(false)}>{source.title}</Link>)}</div>}</div>)}{sending && <div className="chat-message assistant"><p className="typing">Typing...</p></div>}<div ref={endRef} /></div>{error && <div className="chat-error">{error}</div>}<form className="chat-input" onSubmit={submit}><textarea value={input} onChange={(event) => setInput(event.target.value)} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); submit(event) } }} placeholder="Ask about the catalog..." maxLength={500} rows={2} /><button className="btn btn-burgundy" disabled={sending || !input.trim()}>Send</button></form></section>}
  </>
}
