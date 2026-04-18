# Master Data Management System

A comprehensive MDM system with RBAC, data quality assurance, and automated reporting.

## Features

- **CRUD Operations**: Create, read, update, delete master data
- **RBAC**: Role-based access control (admin, editor, viewer)
- **Data Quality**: Validation pipelines with 99% accuracy tracking
- **Audit Logs**: Complete audit trail for all operations
- **Reporting**: Automated reports (CSV, Excel, PDF)
- **Commission/Decommission**: Dataset lifecycle management

## Tech Stack

- FastAPI
- MySQL
- Python
- RBAC with JWT

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database in `.env`:
```
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=mdm_db
```

3. Run the server:
```bash
uvicorn main:app --reload
```

## API Endpoints

### Authentication
- POST `/auth/register` - Register new user
- POST `/auth/login` - Login (get JWT token)
- GET `/auth/me` - Get current user

### Master Data
- POST `/master-data/` - Create data
- GET `/master-data/` - List all data
- GET `/master-data/{id}` - Get single record
- PUT `/master-data/{id}` - Update record
- DELETE `/master-data/{id}` - Delete record
- POST `/master-data/commission/{name}` - Commission dataset
- POST `/master-data/decommission/{name}` - Decommission dataset

### Data Quality
- POST `/data-quality/import` - Import with validation
- POST `/data-quality/validate` - Validate single record
- GET `/data-quality/report/{dataset}` - Quality report

### Reports
- GET `/reports/audit` - Audit logs
- GET `/reports/summary` - System summary
- GET `/reports/export/csv` - Export to CSV
- GET `/reports/export/pdf` - Export to PDF

## Default Roles

| Role    | Permissions |
|---------|-------------|
| admin   | create, read, update, delete, manage_users, view_audit |
| editor  | create, read, update |
| viewer  | read |

## Default Admin

- Username: admin
- Password: admin123