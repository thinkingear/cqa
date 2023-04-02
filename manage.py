#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# VENV_DIR = os.path.join(os.path.dirname(__file__), 'venv')
# SITE_PACKAGES_DIR = os.path.join(VENV_DIR, 'Lib', 'site-packages')
#
# sys.path.append(SITE_PACKAGES_DIR)
#
# from dotenv import load_dotenv


def main():
    """Run administrative tasks."""
    # load_dotenv()  # load the evironment variables in '.env'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cqa.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    # port = os.environ.get("DJANGO_RUNSERVER_PORT", "8000")  # port == 8000 as default
    # argv = sys.argv[:1] + ["runserver", port] + sys.argv[2:]  # sys.argv wrapper
    # execute_from_command_line(argv)
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
