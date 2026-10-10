import re

from django.db.models import Avg, Count
from sklearn.metrics.pairwise import cosine_similarity

from books.models import Author, Book, Genre
from recommendations.engine import _index


def _shorten(text, limit=500):
    text = ' '.join((text or '').split())
    return text if len(text) <= limit else f'{text[:limit].rsplit(" ", 1)[0]}...'


def _book_data(book):
    return {
        'id': book.id,
        'title': book.title,
        'authors': [author.name for author in book.authors.all()],
        'genres': [genre.name for genre in book.genres.all()],
        'avg_rating': round(float(book.avg_rating), 2) if getattr(book, 'avg_rating', None) else None,
        'rating_count': getattr(book, 'rating_count', 0),
        'description': _shorten(book.description),
        'publication_year': book.publication_year,
        'cover_url': book.cover_url,
    }


def retrieve_context(question, user, k=5):
    """Combine exact catalog mentions with TF-IDF matches from the shared index."""
    books = list(Book.objects.annotate(avg_rating=Avg('reviews__rating'), rating_count=Count('reviews', distinct=True)).prefetch_related('authors', 'genres'))
    lowered = question.casefold()
    selected = []
    selected_ids = set()

    for book in books:
        names = [book.title, *[author.name for author in book.authors.all()], *[genre.name for genre in book.genres.all()]]
        if any(name and name.casefold() in lowered for name in names):
            selected.append(book)
            selected_ids.add(book.id)

    indexed_books, matrix, vectorizer = _index()
    if matrix is not None and vectorizer is not None:
        scores = cosine_similarity(vectorizer.transform([question]), matrix).ravel()
        for index in scores.argsort()[::-1]:
            candidate = indexed_books[index]
            if candidate.id not in selected_ids:
                selected.append(next((book for book in books if book.id == candidate.id), candidate))
                selected_ids.add(candidate.id)
            if len(selected) >= k:
                break

    selected = selected[:k]
    context_lines = []
    for book in selected:
        data = _book_data(book)
        context_lines.append(
            f"BOOK id={data['id']} title={data['title']} authors={', '.join(data['authors']) or 'unknown'} "
            f"genres={', '.join(data['genres']) or 'unknown'} year={data['publication_year'] or 'unknown'} "
            f"rating={data['avg_rating'] or 'not rated'} ({data['rating_count']} reviews) description={data['description']}"
        )

    matched_authors = [author.name for author in Author.objects.all() if author.name.casefold() in lowered]
    matched_genres = [genre.name for genre in Genre.objects.all() if genre.name.casefold() in lowered]
    if matched_authors:
        context_lines.append(f"MATCHED AUTHORS: {', '.join(matched_authors[:5])}")
    if matched_genres:
        context_lines.append(f"MATCHED GENRES: {', '.join(matched_genres[:5])}")

    wants_reviews = bool(re.search(r'\b(review|reviews|opinion|opinions|rating|ratings|avis|critique|رأي|تقييم)\b', lowered))
    if wants_reviews and selected:
        comments = selected[0].reviews.order_by('-created_at').values_list('comment', flat=True)[:3]
        comments = [comment for comment in comments if comment]
        if comments:
            context_lines.append(f"RECENT REVIEW COMMENTS FOR {selected[0].title}: {' | '.join(_shorten(comment, 300) for comment in comments)}")

    return {'books': [_book_data(book) for book in selected], 'authors': matched_authors, 'genres': matched_genres, 'text': '\n'.join(context_lines)}
