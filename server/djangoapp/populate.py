"""Compatibility entry point for the course seeding function."""
from django.core.management import call_command

def initiate():
    call_command("seed_cars")
