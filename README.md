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

### Groq chat setup

Create a Groq API key at [console.groq.com](https://console.groq.com/), then paste it only into `backend/.env`:

```env
GROQ_API_KEY=your-key-here
CHAT_MODEL=openai/gpt-oss-120b
CHAT_MAX_TOKENS=600
CHAT_TEMPERATURE=0.3
CHAT_RATE_LIMIT=20/hour
```

`openai/gpt-oss-120b` was verified against the models available to the configured Groq account. The key is backend-only and is never sent to React. If `GROQ_API_KEY` is empty, the backend still starts normally and the chat displays “The assistant isn't configured yet.”

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
| POST | `/api/chat/` | Authenticated catalog-grounded assistant |

The chat request accepts `{"message": "...", "history": [...]}`. Messages are limited to 500 characters and history to the last 10 validated turns. The response contains `reply` and clickable catalog `sources`.

## Recommendation algorithm

1. TF-IDF represents each book using title, authors, repeated genres, and description.
2. Cosine similarity finds books close to a selected book.
3. Personalization uses liked books, favorite genre overlap, and popularity.
4. Reviewed or saved books are excluded.
5. New users receive popular books, with favorite genres used when available.

## How chat RAG works

Before Groq is called, BookWise searches the local PostgreSQL catalog for exact title, author, and genre mentions, then adds TF-IDF matches from the shared recommendation index. It sends only a short structured context containing catalog metadata and selected review comments, together with the last six conversation turns. The prompt tells the model to treat that context as data, avoid invented facts, and answer in the user's language. Conversations are not stored by the backend.
