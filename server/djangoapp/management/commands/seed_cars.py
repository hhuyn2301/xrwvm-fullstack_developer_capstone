"""Idempotently load the course car catalogue."""
import json
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from djangoapp.models import CarMake, CarModel

class Command(BaseCommand):
    help = "Load course car makes/models without deleting existing data."

    @transaction.atomic
    def handle(self, *args, **options):
        source = Path(settings.BASE_DIR) / "database" / "data" / "car_records.json"
        records = json.loads(source.read_text(encoding="utf-8"))["cars"]
        for car in records:
            make, _ = CarMake.objects.get_or_create(
                name=car["make"], defaults={"description": f"{car['make']} vehicles"},
            )
            model, _ = CarModel.objects.update_or_create(
                car_make=make, name=car["model"], year=car["year"],
                dealer_id=car["dealer_id"],
                defaults={"type": car["bodyType"], "mileage": car.get("mileage", 0)},
            )
            model.full_clean()
        self.stdout.write(self.style.SUCCESS(
            f"Car catalogue ready: {CarMake.objects.count()} makes, "
            f"{CarModel.objects.count()} models."
        ))
