# SETUP.md – Local Development Setup

You can run AccrediTrack locally with Docker (recommended) or directly on your machine.

## 1. Prerequisites

- Git
- Docker + docker-compose
- (For non-Docker) Python 3.12+, Node 20+, PostgreSQL

## 2. Environment Files

Copy example env files:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

Adjust values (database credentials, secret key, etc.) as needed.

## 3. Running with Docker

From the repo root:

```bash
docker-compose -f infra/docker-compose.dev.yml up --build
```

This should start:
- Postgres
- Django backend on `http://localhost:8000`
- Next.js frontend on `http://localhost:3000`

Run initial migrations:

```bash
docker-compose -f infra/docker-compose.dev.yml exec backend python manage.py migrate
docker-compose -f infra/docker-compose.dev.yml exec backend python manage.py createsuperuser
```

## 4. Running Without Docker (Optional)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`.

## 5. Seeding Sample Data

Run the seed command to create demo data:

```bash
docker-compose -f infra/docker-compose.dev.yml exec backend python config/manage.py seed_demo_data
```

Or if running without Docker:

```bash
cd backend
python config/manage.py seed_demo_data
```

This creates:
- Roles: SuperAdmin, QAAdmin, DepartmentCoordinator, Viewer
- Departments: Medical, Surgery, Pediatrics
- Users with different roles (see output for credentials)
- A sample ProformaTemplate with sections and items
- Sample assignments for departments

Default credentials:
- SuperAdmin: admin@accreditrack.local / admin123
- QAAdmin: qa@accreditrack.local / qa123
- Coordinator: coordinator.med@accreditrack.local / coord123
