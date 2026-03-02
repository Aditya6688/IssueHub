# IssueHub — A Lightweight Bug Tracker

A minimal, full-stack bug tracker where teams can create projects, file issues, comment on them, and track status with role-based access control.

## Tech Choices & Trade-offs

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Backend** | FastAPI + SQLAlchemy 2.0 | FastAPI provides automatic OpenAPI docs, async support, and fast development. SQLAlchemy 2.0 with mapped_column gives type safety with ORM convenience. |
| **Database** | SQLite (dev) / PostgreSQL (prod) | SQLite requires zero setup for local dev and review. The same SQLAlchemy models work with PostgreSQL in production — just change `DATABASE_URL`. |
| **Migrations** | Alembic | Industry standard for SQLAlchemy migrations; supports autogeneration and upgrade/downgrade. |
| **Auth** | JWT (python-jose + passlib/bcrypt) | Stateless authentication — no server-side session store needed. Tokens are passed via `Authorization: Bearer` header. |
| **Frontend** | React 19 + Vite | Vite provides instant HMR and fast builds. React is the most widely used UI library with a huge ecosystem. |
| **Routing** | react-router-dom v7 | De facto standard for React SPA routing. |
| **HTTP Client** | Axios | Interceptors make it easy to attach JWT tokens and handle 401 redirects globally. |
| **Styling** | Plain CSS | No build-time CSS framework dependency. Clean, responsive styles with CSS variables for theming. |

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, router registration
│   ├── config.py             # Environment-based configuration
│   ├── database.py           # SQLAlchemy engine, session, Base
│   ├── dependencies.py       # Auth utilities (JWT, password hashing)
│   ├── models/               # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── issue.py
│   │   └── comment.py
│   ├── schemas/              # Pydantic request/response schemas
│   │   ├── user.py
│   │   ├── project.py
│   │   ├── issue.py
│   │   └── comment.py
│   └── routes/               # API route handlers
│       ├── auth.py
│       ├── projects.py
│       ├── issues.py
│       └── comments.py
├── alembic/                  # Database migration scripts
├── tests/                    # Pytest test suite
├── seed.py                   # Demo data seeder
├── requirements.txt
└── alembic.ini

frontend/
├── src/
│   ├── main.jsx              # React entry point
│   ├── App.jsx               # Router and layout
│   ├── index.css             # Global styles
│   ├── api/                  # Axios API clients
│   │   ├── client.js
│   │   ├── auth.js
│   │   ├── projects.js
│   │   ├── issues.js
│   │   └── comments.js
│   ├── context/
│   │   └── AuthContext.jsx   # Auth state management
│   ├── components/
│   │   ├── Navbar.jsx
│   │   └── ProtectedRoute.jsx
│   └── pages/
│       ├── LoginPage.jsx
│       ├── SignupPage.jsx
│       ├── ProjectsPage.jsx
│       ├── ProjectDetailPage.jsx
│       └── IssueDetailPage.jsx
├── package.json
└── vite.config.js
```

## Setup Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Run database migrations
python -m alembic upgrade head

# (Optional) Seed demo data
python seed.py
# Demo login: alice@example.com / password123

# Start the backend server
uvicorn app.main:app --reload --port 8000
```

**Environment variables** (optional — sensible defaults are provided):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./issuehub.db` | Database connection string |
| `SECRET_KEY` | `issuehub-dev-secret-key-...` | JWT signing key (change in production!) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token lifetime in minutes |

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The frontend runs on `http://localhost:5173` and proxies API calls to `http://localhost:8000`.

Set `VITE_API_URL` to override the backend URL if needed.

### Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

Tests use an in-memory SQLite database — no external DB setup needed.

**Test coverage:**
- Auth: signup, login, duplicate email, wrong password, protected routes
- Projects: create, list (member scoping), detail, add members, role enforcement
- Issues: CRUD, pagination, filtering by status, text search, role-based status control
- Comments: create, list, auth requirement

## API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register a new user |
| POST | `/api/auth/login` | Login, returns JWT |
| POST | `/api/auth/logout` | Logout (client-side token removal) |
| GET | `/api/auth/me` | Get current user profile |
| POST | `/api/projects` | Create a project (creator becomes maintainer) |
| GET | `/api/projects` | List projects the user belongs to |
| GET | `/api/projects/{id}` | Get project detail with members |
| POST | `/api/projects/{id}/members` | Add member by email (maintainers only) |
| GET | `/api/projects/{id}/issues` | List issues (supports `?q=`, `?status=`, `?priority=`, `?assignee=`, `?sort=`, `?order=`, `?page=`, `?page_size=`) |
| POST | `/api/projects/{id}/issues` | Create an issue |
| GET | `/api/issues/{id}` | Get issue detail |
| PATCH | `/api/issues/{id}` | Update issue (role-based field restrictions) |
| DELETE | `/api/issues/{id}` | Delete issue (reporter or maintainer) |
| GET | `/api/issues/{id}/comments` | List comments for an issue |
| POST | `/api/issues/{id}/comments` | Add a comment |

### Error Format

All errors return structured JSON:
```json
{
  "detail": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  }
}
```

## User Roles

| Role | Permissions |
|------|-------------|
| **Member** | Create issues, update own issues (title/description/priority), comment, view all project issues |
| **Maintainer** | All member permissions + change status, assign issues, add/remove members |

## Known Limitations & Future Improvements

### Current Limitations
- **SQLite in dev**: No concurrent write support; switch to PostgreSQL for production
- **No email verification**: Signup doesn't send verification emails
- **No file attachments**: Issues and comments are text-only
- **No real-time updates**: Must refresh to see changes from other users
- **No activity log**: No audit trail of issue changes

### What I'd Do With More Time
- **WebSocket notifications** for real-time issue updates
- **Rich text editor** (Markdown) for issue descriptions and comments
- **File attachments** with S3/cloud storage
- **Activity timeline** showing all changes to an issue
- **Dashboard** with charts (issues by status, priority distribution)
- **Email notifications** for assignment changes and mentions
- **Bulk operations** (multi-select issues for status change)
- **Docker Compose** setup for one-command deployment
- **E2E tests** with Playwright/Cypress
- **Rate limiting** on auth endpoints
