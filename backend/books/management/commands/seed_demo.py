from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from books.models import Author, Book, Genre, Review
from library.models import ReadingList


class Command(BaseCommand):
    help = 'Create development-only users and sample activity.'

    def handle(self, *args, **options):
        genre, _ = Genre.objects.get_or_create(name='Fantasy')
        author, _ = Author.objects.get_or_create(name='Demo Author')
        books = []
        for title in ['The Green Atlas', 'Letters from Tunis', 'A Practical Cosmos']:
            book, _ = Book.objects.get_or_create(title=title, defaults={'description': f'Demo description for {title}.'})
            book.authors.add(author)
            book.genres.add(genre)
            books.append(book)
        for username in ['demo_reader', 'demo_fan', 'demo_explorer']:
            user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
            if created:
                user.set_password('BookWiseDemo123!')
                user.save()
            user.profile.favorite_genres.add(genre)
        reader = User.objects.get(username='demo_reader')
        Review.objects.get_or_create(user=reader, book=books[0], defaults={'rating': 5, 'comment': 'A great demo review.'})
        ReadingList.objects.get_or_create(user=reader, book=books[1], defaults={'is_favorite': True})
        self.stdout.write(self.style.SUCCESS('Demo data ready. Password: BookWiseDemo123!'))
