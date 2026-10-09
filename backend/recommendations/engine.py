from functools import lru_cache

from django.db.models import Avg, Count
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from books.models import Book


@lru_cache(maxsize=1)
def _index():
    books = list(Book.objects.prefetch_related('authors', 'genres').all())
    texts = [' '.join([book.title, ' '.join(a.name for a in book.authors.all()), ' '.join(g.name for g in book.genres.all()), ' '.join(g.name for g in book.genres.all()), book.description]) for book in books]
    if not texts:
        return books, None, None
    vectorizer = TfidfVectorizer(stop_words='english', max_features=20000, ngram_range=(1, 2))
    return books, vectorizer.fit_transform(texts), vectorizer


def rebuild_index():
    _index.cache_clear()
    _index()


def similar_books(book, limit=6):
    books, matrix, _ = _index()
    if matrix is None or book not in books:
        return []
    index = books.index(book)
    scores = cosine_similarity(matrix[index], matrix).ravel()
    ranked = scores.argsort()[::-1]
    return [{'id': books[i].id, 'title': books[i].title, 'score': round(float(scores[i]), 4)} for i in ranked if books[i].id != book.id][:limit]


def personalized_recommendations(user, limit=10):
    excluded = set(user.reviews.values_list('book_id', flat=True)) | set(user.reading_list.values_list('book_id', flat=True))
    liked = list(user.reviews.filter(rating__gte=4).values_list('book_id', flat=True))
    genres = set(user.profile.favorite_genres.values_list('id', flat=True))
    books = Book.objects.annotate(avg_rating=Avg('reviews__rating'), rating_count=Count('reviews')).prefetch_related('genres')
    candidates = [book for book in books if book.id not in excluded]
    if not candidates:
        return []
    candidates.sort(key=lambda book: (book.avg_rating or 0, book.rating_count), reverse=True)
    return [{'id': book.id, 'title': book.title, 'reason': 'Popular books selected for you'} for book in candidates[:limit]]
