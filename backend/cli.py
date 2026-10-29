"""Operator commands using the canonical Python services (FR-SUP-01, FR-SUP-02, FR-SEC-10, FR-IMP-17)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="MedLiveBD backend operator commands")
    commands = result.add_subparsers(dest="command", required=True)
    create = commands.add_parser("create-staff")
    create.add_argument("--platform", action="store_true")
    create.add_argument("--email", required=True)
    create.add_argument("--name", required=True)
    for option in ["hospital-code", "hospital-name-bn", "hospital-name-en", "kind", "division", "district"]:
        create.add_argument(f"--{option}")
    verify = commands.add_parser("verify-doctor")
    verify.add_argument("--bmdc", required=True)
    reset = commands.add_parser("reset-two-factor")
    reset.add_argument("--email", required=True)
    reset.add_argument("--hospital-code")
    mapping = commands.add_parser("try-mapping")
    mapping.add_argument("--set", required=True, choices=["structure", "patients", "appointments", "records"])
    mapping.add_argument("--type", choices=["department", "doctor", "schedule", "ward", "bed", "staff"])
    mapping.add_argument("--file", required=True)
    return result


def hospital_code(value: str | None) -> str:
    from backend.domain.schemas.auth import hospital_code as schema

    return schema.parse((value or "").strip())


def create_staff(args: argparse.Namespace) -> dict[str, Any]:
    from backend.identity.services.staff_auth import create_first_administrator
    from backend.identity.services.staff_auth import create_platform_administrator

    email, name = args.email.strip(), args.name.strip()
    if "@" not in email or not name:
        raise ValueError("--email and --name must be valid and nonempty.")
    if args.platform:
        if args.hospital_code is not None:
            raise ValueError("--platform belongs to no facility; leave --hospital-code out.")
        return create_platform_administrator(email=email, full_name=name)
    hospital = None
    if args.hospital_name_bn is not None or args.hospital_name_en is not None:
        if args.kind not in ["hospital", "clinic", "diagnostic", "government"]:
            raise ValueError("--kind must be hospital, clinic, diagnostic or government.")
        fields = {"nameBn": args.hospital_name_bn, "nameEn": args.hospital_name_en,
                  "kind": args.kind, "division": args.division, "district": args.district}
        if any(not value or not value.strip() for value in fields.values()):
            raise ValueError("New facilities require both names, kind, division and district.")
        hospital = {key: value.strip() for key, value in fields.items()}
    return create_first_administrator(hospital_code=hospital_code(args.hospital_code), email=email, full_name=name, hospital=hospital)


def try_mapping(args: argparse.Namespace) -> dict[str, Any]:
    from backend.adapters.mapping import mapping_provider
    from backend.core.env import env
    from backend.domain.imports.csv import parse_csv
    from backend.domain.imports.mapping import guess_structure_type
    from backend.domain.imports.mapping import header_looks_like_data
    from backend.domain.imports.mapping import model_mapping_request
    from backend.domain.imports.mapping import profile_columns
    from backend.domain.imports.mapping import propose_mapping
    from backend.domain.imports.mapping import target_of
    from backend.domain.imports.mapping import with_model_suggestions

    table = parse_csv(Path(args.file).read_text(encoding="utf-8-sig"))
    if isinstance(table, str):
        raise ValueError(f"The file could not be read as CSV: {table}.")
    if header_looks_like_data(table["header"]):
        raise ValueError("The first row reads as data, not headings; nothing was sent.")
    columns = profile_columns(table)
    row_type = args.type or (guess_structure_type(columns) if args.set == "structure" else None)
    target = target_of(args.set, row_type)
    if target is None:
        raise ValueError("The structure type could not be determined; give --type.")
    rules = propose_mapping(target, columns)
    request = model_mapping_request(target, columns, rules)
    result = {"rows": len(table["rows"]), "columns": len(columns), "rules": rules, "request": request}
    if request is not None and env().MAPPING_PROVIDER != "off":
        answer = mapping_provider().propose(request)
        result["suggestions"] = (
            with_model_suggestions(rules, request, answer["suggestions"])
            if answer.get("kind") != "unavailable" else answer
        )
    return result


def execute(args: argparse.Namespace) -> Any:
    if args.command == "create-staff":
        return create_staff(args)
    if args.command == "try-mapping":
        return try_mapping(args)
    if args.command == "verify-doctor":
        from backend.hospital.services.hospital_settings import verify_doctor
        from backend.domain.schemas.settings import bmdc_number

        number = bmdc_number.parse(args.bmdc)
        name = verify_doctor(number)
        if name is None:
            raise ValueError("No doctor has that BMDC registration number.")
        return {"verified": number, "name": name}
    from backend.identity.services.staff_auth import reset_two_factor_from_server

    email = args.email.strip()
    if not email:
        raise ValueError("--email is required.")
    result = reset_two_factor_from_server(email=email, hospital_code=None if args.hospital_code is None else hospital_code(args.hospital_code))
    if result is None:
        raise ValueError("No account has that email.")
    return result


def main(argv: list[str] | None = None) -> None:
    args = parser().parse_args(argv)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.core.settings")
    import django

    django.setup()
    try:
        print(json.dumps(execute(args), ensure_ascii=False, indent=2))
    finally:
        from django.db import connections

        connections.close_all()


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1) from None
