import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { addReview, getBook, getReviews, getSimilar } from '../services/books'
import { addToLibrary } from '../services/library'
import { useAuth } from '../context/useAuth'
import BookCard from '../components/BookCard'
import Spinner from '../components/Spinner'

function askAssistant(question) {
  window.dispatchEvent(new CustomEvent('bookwise:chat-question', { detail: question }))
}

export default function Details() {
  const { id } = useParams()
  const { user } = useAuth()
  const [book, setBook] = useState(null)
  const [reviews, setReviews] = useState([])
  const [similar, setSimilar] = useState([])
  const [comment, setComment] = useState('')
  const [rating, setRating] = useState(5)

  useEffect(() => {
    Promise.all([getBook(id), getReviews(id), getSimilar(id)]).then(([bookResponse, reviewsResponse, similarResponse]) => {
      setBook(bookResponse.data)
      setReviews(reviewsResponse.data)
      setSimilar(similarResponse.data || [])
    })
  }, [id])

  if (!book) return <main className="container py-5"><Spinner /></main>

  const submitReview = async (event) => {
    event.preventDefault()
    const response = await addReview(id, { rating, comment })
    setReviews([response.data, ...reviews])
    setComment('')
  }
  const title = book.title

  return <main className="container py-5"><div className="detail-layout"><div className="cover cover-large">{book.cover_url ? <img src={book.cover_url} alt={title} /> : <span>{title[0]}</span>}</div><div><p className="eyebrow">Book detail</p><h1>{title}</h1><p className="muted">{book.authors.map((author) => author.name).join(', ')}</p><p>{book.description}</p><p className="rating">{book.avg_rating ? Number(book.avg_rating).toFixed(1) : '—'} / 5 · {book.rating_count} reviews</p>{user && <button className="btn btn-green" onClick={() => addToLibrary({ book: book.id })}>Add to library</button>}{user && <div className="quick-questions"><p className="eyebrow">Ask the assistant</p><button onClick={() => askAssistant(`Summarize the book "${title}"`)}>Summarize this book</button><button onClick={() => askAssistant(`Who is the author of "${title}"?`)}>Who is the author?</button><button onClick={() => askAssistant(`What books are similar to "${title}"?`)}>Similar books?</button></div>}</div></div><section className="detail-section"><h2>Reviews</h2>{user && <form onSubmit={submitReview} className="review-form"><select value={rating} onChange={(event) => setRating(Number(event.target.value))}>{[5, 4, 3, 2, 1].map((number) => <option key={number} value={number}>{number} stars</option>)}</select><textarea value={comment} onChange={(event) => setComment(event.target.value)} placeholder="Share a thought" /><button className="btn btn-burgundy">Post review</button></form>}{reviews.map((review) => <article className="review" key={review.id}><strong>{review.username}</strong><span>{review.rating} / 5</span><p>{review.comment}</p></article>)}</section>{similar.length > 0 && <section><h2>Similar books</h2><div className="book-grid">{similar.map((item) => <BookCard key={item.id} book={item} />)}</div></section>}</main>
}
