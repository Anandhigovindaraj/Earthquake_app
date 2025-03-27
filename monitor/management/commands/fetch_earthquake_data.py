import requests
from django.core.management.base import BaseCommand
from monitor.models import Earthquake
from datetime import datetime, timezone
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Fetch real-time earthquake data from USGS'

    # List of USGS GeoJSON feed URLs
    FEED_URLS = [
        'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson',
        'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson',
        'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson'
    ]

    def handle(self, *args, **kwargs):
        # Loop through each feed URL
        for url in self.FEED_URLS:
            self.stdout.write(self.style.NOTICE(f"Fetching data from {url}..."))

            try:
                # Fetch the earthquake data from the URL
                response = requests.get(url)
                response.raise_for_status()  # Raise error for invalid responses (e.g., 404, 500)
            except requests.RequestException as e:
                self.stderr.write(self.style.ERROR(f"Error fetching data from {url}: {e}"))
                continue  # Continue to the next feed URL if there is an error

            try:
                # Parse the JSON response
                data = response.json()
                features = data.get('features', [])
                if not features:
                    self.stderr.write(self.style.WARNING(f"No earthquake data found in the USGS feed from {url}."))
                    continue
            except ValueError as e:
                self.stderr.write(self.style.ERROR(f"Error parsing JSON response from {url}: {e}"))
                continue

            # Prepare a list of earthquake objects to save in bulk
            earthquakes_to_save = []

            # Iterate over each feature (earthquake) in the response
            for feature in features:
                properties = feature.get('properties', {})
                geometry = feature.get('geometry', {})

                # Extract necessary fields
                place = properties.get('place')
                magnitude = properties.get('mag')
                timestamp = properties.get('time')
                coordinates = geometry.get('coordinates', [])

                if not place or magnitude is None or not timestamp or len(coordinates) < 2:
                    self.stderr.write(self.style.WARNING(f"Skipping malformed entry: {feature}"))
                    continue  # Skip malformed entries

                # Convert timestamp (milliseconds) to a Python datetime object
                time = datetime.fromtimestamp(timestamp / 1000.0, tz=timezone.utc)
                latitude = coordinates[1]
                longitude = coordinates[0]

                # Check for duplicates before adding to the list
                if not Earthquake.objects.filter(place=place, time=time).exists():
                    earthquake = Earthquake(
                        place=place,
                        magnitude=magnitude,
                        time=time,
                        latitude=latitude,
                        longitude=longitude,
                    )
                    earthquakes_to_save.append(earthquake)
                    self.stdout.write(self.style.SUCCESS(f"Queued earthquake: {place} at {time}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Duplicate earthquake skipped: {place} at {time}"))

            # Bulk save all new earthquake records
            if earthquakes_to_save:
                try:
                    Earthquake.objects.bulk_create(earthquakes_to_save)
                    self.stdout.write(self.style.SUCCESS(f"Successfully saved {len(earthquakes_to_save)} earthquakes."))
                except IntegrityError as e:
                    self.stderr.write(self.style.ERROR(f"Error saving earthquake data: {e}"))
            else:
                self.stdout.write(self.style.WARNING("No new earthquakes to save."))

        self.stdout.write(self.style.SUCCESS('Earthquake data fetching and saving process completed.'))
