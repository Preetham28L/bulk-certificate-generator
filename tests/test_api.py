import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.database import SessionLocal
from app.models import Job, Recipient
from services.job_processor import process_job


@pytest.fixture
def client():
    return TestClient(app)


def test_create_job(client):
    response = client.post(
        "/jobs",
        json={
            "event_name": "AI Workshop 2026",
            "issuer_name": "Reva University",
            "recipients": [
                {
                    "name": "John Doe",
                    "email": "john@example.com",
                },
                {
                    "name": "Jane Doe",
                    "email": "jane@example.com",
                },
            ],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "job_id" in data
    assert data["status"] == "PENDING"
    assert data["total_recipients"] == 2


def test_get_job_status(client):
    response = client.post(
        "/jobs",
        json={
            "event_name": "AI Workshop 2026",
            "issuer_name": "Reva University",
            "recipients": [
                {
                    "name": "Status User",
                    "email": "status@example.com",
                }
            ],
        },
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    response = client.get(
        f"/jobs/{job_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["event_name"] == "AI Workshop 2026"
    assert data["issuer_name"] == "Reva University"
    assert data["total_recipients"] == 1


def test_individual_recipient_failure(monkeypatch):
    from pathlib import Path

    def fake_generate_certificate(
        recipient_name,
        event_name,
        issuer_name,
        output_path,
    ):
        if recipient_name == "Failed User":
            raise Exception("Certificate generation failed")

        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(output_path, "wb") as file:
            file.write(b"fake pdf content")

        return output_path

    monkeypatch.setattr(
        "services.job_processor.generate_certificate",
        fake_generate_certificate,
    )

    db = SessionLocal()

    job = Job(
        event_name="AI Workshop 2026",
        issuer_name="Reva University",
        total_recipients=2,
        status="PENDING",
    )

    db.add(job)
    db.flush()

    db.add(
        Recipient(
            job_id=job.id,
            name="Success User",
            email="success@example.com",
            status="PENDING",
        )
    )

    db.add(
        Recipient(
            job_id=job.id,
            name="Failed User",
            email="failed@example.com",
            status="PENDING",
        )
    )

    db.commit()

    job_id = job.id

    db.close()

    process_job(job_id)

    db = SessionLocal()

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    recipients = (
        db.query(Recipient)
        .filter(Recipient.job_id == job_id)
        .all()
    )

    assert job.successful_count == 1
    assert job.failed_count == 1
    assert job.status == "COMPLETED_WITH_ERRORS"

    success_recipient = next(
        r for r in recipients
        if r.name == "Success User"
    )

    failed_recipient = next(
        r for r in recipients
        if r.name == "Failed User"
    )

    assert success_recipient.status == "SUCCESS"

    assert failed_recipient.status == "FAILED"

    assert (
        failed_recipient.error_message
        == "Certificate generation failed"
    )

    db.close()


def test_list_certificates(client, monkeypatch):
    from pathlib import Path

    def fake_generate_certificate(
        recipient_name,
        event_name,
        issuer_name,
        output_path,
    ):
        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(output_path, "wb") as file:
            file.write(b"%PDF-1.4 fake certificate")

        return output_path

    monkeypatch.setattr(
        "services.job_processor.generate_certificate",
        fake_generate_certificate,
    )

    response = client.post(
        "/jobs",
        json={
            "event_name": "AI Workshop 2026",
            "issuer_name": "Reva University",
            "recipients": [
                {
                    "name": "Certificate User",
                    "email": "certificate@example.com",
                }
            ],
        },
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    db = SessionLocal()

    recipient = (
        db.query(Recipient)
        .filter(Recipient.job_id == job_id)
        .first()
    )

    recipient_id = recipient.id

    db.close()

    response = client.get(
        f"/jobs/{job_id}/certificates"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["job_id"] == job_id
    assert data["total_certificates"] == 1
    assert len(data["certificates"]) == 1

    certificate = data["certificates"][0]

    assert certificate["recipient_id"] == recipient_id
    assert certificate["recipient_name"] == "Certificate User"
    assert certificate["status"] == "SUCCESS"
    assert certificate["certificate_path"] is not None


def test_download_certificate(client, monkeypatch):
    from pathlib import Path

    def fake_generate_certificate(
        recipient_name,
        event_name,
        issuer_name,
        output_path,
    ):
        Path(output_path).parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with open(output_path, "wb") as file:
            file.write(b"%PDF-1.4 fake certificate")

        return output_path

    monkeypatch.setattr(
        "services.job_processor.generate_certificate",
        fake_generate_certificate,
    )

    response = client.post(
        "/jobs",
        json={
            "event_name": "AI Workshop 2026",
            "issuer_name": "Reva University",
            "recipients": [
                {
                    "name": "Test User",
                    "email": "test@example.com",
                }
            ],
        },
    )

    assert response.status_code == 200

    job_id = response.json()["job_id"]

    db = SessionLocal()

    recipient = (
        db.query(Recipient)
        .filter(Recipient.job_id == job_id)
        .first()
    )

    recipient_id = recipient.id

    db.close()

    response = client.get(
        f"/certificates/{recipient_id}"
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")