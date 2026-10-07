# Bulk Certificate Generator

A FastAPI-based backend system for generating certificates in bulk from recipient data.

The system creates a job for a list of recipients, processes certificates in the background, tracks individual recipient status, and provides APIs to monitor jobs and download generated certificates.

## Features

- Bulk certificate generation
- Background job processing with FastAPI BackgroundTasks
- Individual recipient processing and status tracking
- Automatic success/failure tracking
- PDF certificate generation
- Job progress monitoring
- Certificate listing and download API
- Input validation using Pydantic
- SQLite database using SQLAlchemy
- Environment-based configuration
- Automated API and service tests with pytest
- Interactive Swagger API documentation

## Tech Stack

- Python
- FastAPI
- SQLAlchemy
- Pydantic
- SQLite
- ReportLab
- Pytest
- Uvicorn

## Project Structure

```text
bulk-certificate-generator/
│
├── app/
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   ├── models.py
│   └── schemas.py
│
├── services/
│   ├── certificate_generator.py
│   └── job_processor.py
│
├── tests/
│   ├── test_api.py
│   └── test_certificate_generator.py
│
├── certificates/
│   └── Generated PDF certificates
│
├── .env
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md