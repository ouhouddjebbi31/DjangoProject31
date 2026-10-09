# BookWise AI

BookWise AI is a Django REST + React platform for discovering books, managing a private reading list, writing reviews, and receiving recommendations.

## Prerequisites

- Python 3.11+
- Node.js LTS and npm
- PostgreSQL running on `localhost:5432`

## Backend setup

```powershell
cd backend
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env`, then set the real PostgreSQL database name, user, and password. Never commit `.env`.

```powershell
python manage.py check
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

For a Goodreads-style CSV with descriptions and genres:

```powershell
python manage.py import_books --file dataset\data\books.csv --limit 3000
```

Use a dataset such as Kaggle's Best Books Ever and place the CSV in `backend/dataset/data/`. Book-Crossing has no descriptions, so it cannot power TF-IDF recommendations.

Demo users created by `seed_demo` use the development-only password `BookWiseDemo123!`.

## Frontend setup

```powershell
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173`. The backend admin is at `http://127.0.0.1:8000/admin/`.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register/` | Register |
| POST | `/api/auth/token/` | Obtain JWT |
| GET/PATCH | `/api/me/` | Current profile |
| GET | `/api/books/` | Search, filter and order books |
| GET/POST | `/api/books/{id}/reviews/` | List or create one review |
| GET | `/api/books/{id}/similar/` | Similar books |
| GET/POST | `/api/reading-list/` | Private reading list |
| GET | `/api/recommendations/` | Personalized recommendations |

## Recommendation algorithm

1. TF-IDF represents each book using title, authors, repeated genres, and description.
2. Cosine similarity finds books close to a selected book.
3. Personalization uses liked books, favorite genre overlap, and popularity.
4. Reviewed or saved books are excluded.
5. New users receive popular books, with favorite genres used when available.
