import { useEffect, useState } from 'react'
import { getBooks } from '../services/books'
import BookCard from '../components/BookCard'
import Spinner from '../components/Spinner'

export default function Explore() {
  const [query, setQuery] = useState('')
  const [books, setBooks] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let active = true
    getBooks({}).then((response) => { if (active) setBooks(response.data.results || []) }).finally(() => { if (active) setLoading(false) })
    return () => { active = false }
  }, [])

  const search = async (event) => {
    event.preventDefault()
    setLoading(true)
    try {
      const response = await getBooks(query ? { search: query } : {})
      setBooks(response.data.results || [])
    } finally { setLoading(false) }
  }

  return <main className="container py-5"><p className="eyebrow">The catalogue</p><h1>Explore books</h1><form className="search-row my-4" onSubmit={search}><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search by title or author" /><button className="btn btn-burgundy">Search</button></form>{loading ? <Spinner /> : books.length ? <div className="book-grid">{books.map((book) => <BookCard key={book.id} book={book} />)}</div> : <p className="muted">No books found yet.</p>}</main>
}
