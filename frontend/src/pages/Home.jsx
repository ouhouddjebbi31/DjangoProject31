import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { getBooks } from '../services/books'
import BookCard from '../components/BookCard'
import Spinner from '../components/Spinner'
export default function Home() { const [books, setBooks] = useState([]); const [loading, setLoading] = useState(true); useEffect(() => { getBooks({ ordering: '-avg_rating' }).then((r) => setBooks(r.data.results || [])).finally(() => setLoading(false)) }, []); return <main><section className="hero-band"><div className="container"><p className="eyebrow">Read with intention</p><h1>Find the next book<br /><em>worth your time.</em></h1><p className="lead">BookWise AI turns your reading history into thoughtful recommendations.</p><Link className="btn btn-burgundy" to="/books">Browse the library</Link></div></section><section className="container py-5"><div className="section-heading"><div><p className="eyebrow">Curated shelf</p><h2>Popular this week</h2></div><Link to="/books">See all books</Link></div>{loading ? <Spinner /> : <div className="book-grid">{books.slice(0, 8).map((book) => <BookCard key={book.id} book={book} />)}</div>}</section></main> }
