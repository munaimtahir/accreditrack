# AccrediFy

**Compliance and Accreditation Management Platform**

AccrediFy is a comprehensive platform for medical institutions, laboratories, and universities to manage their compliance and accreditation processes.

## Features

- **Project Management**: Create and manage accreditation projects (PHC Lab, PMDC, CPSP, UTRMC, etc.)
- **Indicator Tracking**: Manage compliance indicators and requirements with detailed checklists
- **Evidence Management**: Upload and link supporting documents, URLs, and notes
- **Compliance Progress**: Track status and completion of requirements
- **AI Assistant**: Powered by Google Gemini API for:
  - Analyzing compliance checklists
  - Categorizing indicators
  - Generating compliance summaries
  - Creating compliance guides
  - Converting documents
  - Answering regulatory questions
  - Analyzing and optimizing tasks

## Technology Stack

### Backend
- Python 3.11+
- Django 5.0+
- Django REST Framework
- JWT Authentication (djangorestframework-simplejwt)
- PostgreSQL
- Gunicorn
- Google Gemini AI API

### Frontend
- React 18
- TypeScript
- Vite
- React Router
- Axios

### Infrastructure
- Docker & Docker Compose
- Nginx (reverse proxy)
- PostgreSQL 16

## Architecture

```
Browser
  ↓
NGINX (port 80)
  ├── Serves React frontend (/)
  └── Proxies /api → Django backend (port 8000)
        ↓
     PostgreSQL (port 5432)
        ↓
     Gemini API (AI features)
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Git

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd accreditrack
```

2. Create environment file:
```bash
cp .env.template .env
```

3. Edit `.env` and configure:
```env
DB_PASSWORD=your_secure_password
DJANGO_SECRET_KEY=your_secret_key_here
GEMINI_API_KEY=your_gemini_api_key  # Optional for AI features
```

To generate a Django secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

4. Build and start services:
```bash
docker compose up --build
```

5. Create a superuser (in a new terminal):
```bash
docker compose exec backend python manage.py createsuperuser
```

6. Access the application:
- **Frontend**: http://localhost
- **API Documentation**: http://localhost/api/docs/
- **Admin Panel**: http://localhost/admin/

## API Endpoints

### Authentication
- `POST /api/auth/token/` - Obtain JWT token
- `POST /api/auth/token/refresh/` - Refresh JWT token

### Core CRUD
- `GET/POST /api/projects/` - List/Create projects
- `GET/PUT/PATCH/DELETE /api/projects/{id}/` - Retrieve/Update/Delete project
- `GET/POST /api/indicators/` - List/Create indicators
- `GET/PUT/PATCH/DELETE /api/indicators/{id}/` - Retrieve/Update/Delete indicator
- `GET/POST /api/evidence/` - List/Create evidence
- `GET/PUT/PATCH/DELETE /api/evidence/{id}/` - Retrieve/Update/Delete evidence

### AI Endpoints (Require Gemini API Key)
- `POST /api/analyze-checklist/` - Analyze compliance checklists
- `POST /api/analyze-categorization/` - Categorize indicators
- `POST /api/ask-assistant/` - Ask compliance questions
- `POST /api/report-summary/` - Generate compliance summaries
- `POST /api/convert-document/` - Convert document formats
- `POST /api/compliance-guide/` - Get compliance guides
- `POST /api/analyze-tasks/` - Analyze and optimize tasks

## Data Models

### Project
- id
- name
- description
- created_at
- updated_at

### Indicator
- id
- project (FK)
- area
- regulation_or_standard
- requirement
- evidence_required
- responsible_person
- frequency
- status (pending/partial/compliant/non_compliant)
- assigned_to
- created_at
- updated_at

### Evidence
- id
- indicator (FK)
- title
- file (upload)
- url (optional)
- notes (optional)
- uploaded_at

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Running Tests

```bash
# Backend tests
docker compose exec backend python manage.py test

# Frontend tests (when implemented)
cd frontend
npm test
```

## Environment Variables

See `.env.template` for all available configuration options.

### Required Variables
- `DB_PASSWORD` - PostgreSQL database password
- `DJANGO_SECRET_KEY` - Django secret key for cryptographic signing

### Optional Variables
- `GEMINI_API_KEY` - Google Gemini API key (required for AI features)
- `DEBUG` - Enable debug mode (default: False)
- `ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `CORS_ALLOWED_ORIGINS` - Comma-separated list of allowed CORS origins

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Configure `ALLOWED_HOSTS` with your domain
3. Set strong passwords and secret keys
4. Consider using a managed PostgreSQL service
5. Set up SSL/TLS certificates for HTTPS
6. Configure proper backup strategies
7. Monitor application logs and metrics

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost/api/docs/`
- OpenAPI Schema: `http://localhost/api/schema/`

## License

See LICENSE file for details.

## Support

For issues, questions, or contributions, please open an issue on the repository.
