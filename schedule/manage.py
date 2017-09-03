#!/usr/bin/env python

import sys
import os

if __name__ == "__main__":
    from configurations.management import execute_from_command_line

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings.test')
    os.environ.setdefault('DJANGO_CONFIGURATION', 'Test')
    execute_from_command_line(sys.argv)
