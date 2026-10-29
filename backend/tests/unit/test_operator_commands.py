"""Operator entry points keep using the canonical services (FR-SUP-01, FR-SUP-02, FR-SEC-10, FR-IMP-17)."""

import json
from types import SimpleNamespace

import pytest

from backend.cli import execute, parser


def test_platform_creation_rejects_a_hospital_before_writing(monkeypatch):
    from backend.identity.services import staff_auth

    monkeypatch.setattr(staff_auth, "create_platform_administrator", lambda **kwargs: pytest.fail("unexpected write"))
    args = parser().parse_args(["create-staff", "--platform", "--hospital-code", "DEMO", "--email", "operator@example.test", "--name", "Synthetic Operator"])
    with pytest.raises(ValueError, match="belongs to no facility"):
        execute(args)


def test_doctor_verification_normalizes_and_calls_the_existing_service(monkeypatch):
    from backend.hospital.services import hospital_settings

    called = []
    monkeypatch.setattr(hospital_settings, "verify_doctor", lambda number: called.append(number) or "Synthetic Doctor")
    assert execute(parser().parse_args(["verify-doctor", "--bmdc", " a-12345 "])) == {"verified": "A-12345", "name": "Synthetic Doctor"}
    assert called == ["A-12345"]


def test_two_factor_reset_preserves_the_service_scope(monkeypatch):
    from backend.identity.services import staff_auth

    called = []
    monkeypatch.setattr(staff_auth, "reset_two_factor_from_server", lambda **kwargs: called.append(kwargs) or {"fullName": "Synthetic Operator"})
    execute(parser().parse_args(["reset-two-factor", "--email", "operator@example.test", "--hospital-code", " demo "]))
    assert called == [{"email": "operator@example.test", "hospital_code": "DEMO"}]


def test_mapping_preview_contains_no_values_from_input_rows(tmp_path, monkeypatch):
    from backend.core import env

    monkeypatch.setattr(env, "env", lambda: SimpleNamespace(MAPPING_PROVIDER="off"))
    source = tmp_path / "synthetic.csv"
    source.write_text("name,gender,phone\nSynthetic Private Person,male,01712345678\n", encoding="utf8")
    result = execute(parser().parse_args(["try-mapping", "--set", "patients", "--file", str(source)]))
    assert result["rows"] == 1
    assert "Synthetic Private Person" not in json.dumps(result)
    assert "01712345678" not in json.dumps(result)
