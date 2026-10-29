#!/usr/bin/env python
"""Django's command line for the MedLiveBD API (`python manage.py help`)."""

import os
import sys
from pathlib import Path

# Direct script invocation must resolve the backend package from the repository.
sys.path[0] = str(Path(__file__).resolve().parent.parent)


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.core.settings")
    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
