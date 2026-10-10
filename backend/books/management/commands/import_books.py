import ast
import re
from pathlib import Path

import pandas as pd
from django.core.management.base import BaseCommand

from books.models import Author, Book, Genre
from recommendations.engine import rebuild_index

# Adapt these values to the exact column names in the downloaded CSV.
COLUMN_MAPPING = {
    'title': 'title',
    'authors': 'author',
    'description': 'description',
    'genres': 'genres',
    'isbn': 'ISBN',
    'year': 'publishDate',
    'cover_url': 'coverImg',
}


def clean_text(value):
    if pd.isna(value):
        return ''
    return re.sub(r'\s+', ' ', str(value or '')).strip()


def parse_list(value):
    text = clean_text(value)
    if not text:
        return []
    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [clean_text(item) for item in parsed if clean_text(item)]
    except (ValueError, SyntaxError):
        pass
    return [clean_text(item) for item in re.split(r'[,;|]', text) if clean_text(item)]


def parse_year(value):
    text = clean_text(value)
    if not text:
        return None
    parsed = pd.to_datetime(text, errors='coerce')
    if not pd.isna(parsed):
        return int(parsed.year)
    year_match = re.search(r'(\d{4})', text)
    return int(year_match.group(1)) if year_match else None


class Command(BaseCommand):
    help = 'Import books from a Goodreads-style CSV file.'

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True)
        parser.add_argument('--limit', type=int, default=3000)

    def handle(self, *args, **options):
        path = Path(options['file'])
        if not path.exists():
            self.stderr.write(self.style.ERROR(f'File not found: {path}'))
            return
        frame = pd.read_csv(path, nrows=options['limit'])
        imported = skipped = 0
        for _, row in frame.iterrows():
            title = clean_text(row.get(COLUMN_MAPPING['title']))
            description = clean_text(row.get(COLUMN_MAPPING['description']))
            if not title or not description:
                skipped += 1
                continue
            isbn = clean_text(row.get(COLUMN_MAPPING['isbn'])) or None
            authors = parse_list(row.get(COLUMN_MAPPING['authors'])) or ['Unknown']
            first_author = authors[0]
            publication_year = parse_year(row.get(COLUMN_MAPPING['year']))
            cover_url = clean_text(row.get(COLUMN_MAPPING['cover_url']))
            if isbn and Book.objects.filter(isbn=isbn).exists():
                existing = Book.objects.get(isbn=isbn)
                changed = False
                if existing.publication_year is None and publication_year:
                    existing.publication_year = publication_year
                    changed = True
                if not existing.cover_url and cover_url:
                    existing.cover_url = cover_url
                    changed = True
                if changed:
                    existing.save(update_fields=['publication_year', 'cover_url'])
                skipped += 1
                continue
            existing = Book.objects.filter(title__iexact=title, authors__name__iexact=first_author).first()
            if existing:
                changed = False
                if existing.publication_year is None and publication_year:
                    existing.publication_year = publication_year
                    changed = True
                if not existing.cover_url and cover_url:
                    existing.cover_url = cover_url
                    changed = True
                if changed:
                    existing.save(update_fields=['publication_year', 'cover_url'])
                skipped += 1
                continue
            book = Book.objects.create(title=title, description=description, isbn=isbn, publication_year=publication_year, cover_url=cover_url)
            book.authors.set([Author.objects.get_or_create(name=name)[0] for name in authors])
            book.genres.set([Genre.objects.get_or_create(name=name)[0] for name in parse_list(row.get(COLUMN_MAPPING['genres']))])
            imported += 1
        rebuild_index()
        self.stdout.write(self.style.SUCCESS(f'Imported: {imported}; skipped: {skipped}'))
