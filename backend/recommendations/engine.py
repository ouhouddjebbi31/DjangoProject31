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
    return [_book_payload(books[i], round(float(scores[i]), 4), 'Similar themes and description') for i in ranked if books[i].id != book.id][:limit]


def _book_payload(book, score, reason):
    return {
        'id': book.id,
        'title': book.title,
        'description': book.description,
        'cover_url': book.cover_url,
        'publication_year': book.publication_year,
        'authors': [{'id': author.id, 'name': author.name} for author in book.authors.all()],
        'genres': [{'id': genre.id, 'name': genre.name} for genre in book.genres.all()],
        'avg_rating': round(float(book.avg_rating), 2) if getattr(book, 'avg_rating', None) else None,
        'rating_count': getattr(book, 'rating_count', 0),
        'score': score,
        'reason': reason,
    }


def personalized_recommendations(user, limit=10):
    excluded = set(user.reviews.values_list('book_id', flat=True)) | set(user.reading_list.values_list('book_id', flat=True))
    liked_reviews = user.reviews.filter(rating__gte=4).select_related('book').prefetch_related('book__genres', 'book__authors')
    favorite_entries = user.reading_list.filter(is_favorite=True).select_related('book').prefetch_related('book__genres', 'book__authors')
    liked_books = list({book.id: book for book in [review.book for review in liked_reviews] + [entry.book for entry in favorite_entries]}.values())
    favorite_genres = set(user.profile.favorite_genres.values_list('id', flat=True))
    liked_genres = {genre.id for book in liked_books for genre in book.genres.all()}
    target_genres = favorite_genres | liked_genres
    books, matrix, _ = _index()
    annotated = Book.objects.filter(id__in=[book.id for book in books]).annotate(
        avg_rating=Avg('reviews__rating'), rating_count=Count('reviews', distinct=True)
    ).prefetch_related('authors', 'genres')
    metadata = {book.id: book for book in annotated}
    if not books:
        return []
    liked_indices = [books.index(book) for book in liked_books if book in books]
    similarity_scores = {}
    if matrix is not None and liked_indices:
        similarities = cosine_similarity(matrix[liked_indices], matrix)
        for index, book in enumerate(books):
            similarity_scores[book.id] = float(similarities[:, index].max())
    popularity_values = [float(getattr(metadata.get(book.id), 'avg_rating', None) or 0) for book in books]
    max_popularity = max(popularity_values or [1]) or 1
    candidates = [book for book in books if book.id not in excluded]
    if not candidates:
        return []
    scored = []
    for book in candidates:
        details = metadata.get(book.id)
        book_genres = {genre.id for genre in book.genres.all()}
        genre_score = len(book_genres & target_genres) / max(len(target_genres), 1)
        popularity = (float(getattr(details, 'avg_rating', None) or 0) / max_popularity) if details else 0
        score = 0.6 * similarity_scores.get(book.id, 0) + 0.25 * genre_score + 0.15 * popularity
        genre_names = ', '.join(genre.name for genre in book.genres.all()[:3])
        if liked_books and similarity_scores.get(book.id, 0) > 0:
            reason = f"Because you liked {liked_books[0].title}" + (f" and it shares {genre_names}" if genre_names else '')
        elif genre_names and book_genres & target_genres:
            reason = f"It matches your interests in {genre_names}"
        else:
            reason = 'A highly rated book from the community'
        scored.append((score, details or book, reason))
    scored.sort(key=lambda item: item[0], reverse=True)
    return [_book_payload(book, round(score, 4), reason) for score, book, reason in scored[:limit]]
