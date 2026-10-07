from services.certificate_generator import generate_certificate


def test_generate_certificate(tmp_path):
    output_file = tmp_path / "certificate.pdf"

    result = generate_certificate(
        recipient_name="Preetham",
        event_name="AI Workshop 2026",
        issuer_name="Reva University",
        output_path=str(output_file),
    )

    assert output_file.exists()
    assert result == str(output_file)
    assert output_file.stat().st_size > 0