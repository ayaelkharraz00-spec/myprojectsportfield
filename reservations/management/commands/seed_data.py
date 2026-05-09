"""
python manage.py seed_data
Populates the database with demo sports, fields, users, and reservations.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from reservations.models import Sport, Terrain, Reservation
import datetime


class Command(BaseCommand):
    help = 'Seeds the database with demo data.'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding…\n')

        # Sports
        sports_data = [
            ('Football', 22), ('Tennis', 4), ('Basketball', 10),
            ('Padel', 4), ('Volleyball', 12),
        ]
        sports = {}
        for name, cap in sports_data:
            obj, created = Sport.objects.get_or_create(name=name, defaults={'max_capacity': cap})
            sports[name] = obj
            if created: self.stdout.write(f'  ✅ Sport: {name}')

        # Terrains
        terrains_data = [
            ('Field A',      'gazon',        'Football',   True),
            ('Field B',      'synthetique',  'Football',   True),
            ('Field C',      'gazon',        'Football',   False),
            ('Court 1',      'terre_battue', 'Tennis',     True),
            ('Court 2',      'synthetique',  'Tennis',     True),
            ('Arena A',      'parquet',      'Basketball', True),
            ('Padel Court',  'synthetique',  'Padel',      True),
            ('Beach Court',  'synthetique',  'Volleyball', True),
        ]
        terrains = {}
        for name, surface, sport_name, avail in terrains_data:
            obj, created = Terrain.objects.get_or_create(name=name, defaults={
                'surface_type': surface, 'sport': sports[sport_name], 'availability': avail
            })
            terrains[name] = obj
            if created: self.stdout.write(f'  ✅ Terrain: {name}')

        # Users
        for username, pw in [('ayaka','pass1234'),('loli','pass1234')]:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(username=username, password=pw)
                self.stdout.write(f'  ✅ User: {username} / {pw}')

        # Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@sportfield.com', 'admin123')
            self.stdout.write('  ✅ Superuser: admin / admin123')

        # Sample reservations
        ayaka = User.objects.get(username='ayaka')
        loli   = User.objects.get(username='loli')
        today = datetime.date.today()
        samples = [
            (terrains['Field A'],     ayaka, today + datetime.timedelta(days=1), datetime.time(10,0), 2),
            (terrains['Court 1'],     loli,   today + datetime.timedelta(days=1), datetime.time(14,0), 1),
            (terrains['Padel Court'], ayaka,   today + datetime.timedelta(days=7), datetime.time(16,0), 1),
        ]
        for terrain, user, date, start, dur in samples:
            if not Reservation.objects.filter(terrain=terrain, date=date, start_time=start).exists():
                try:
                    r = Reservation(terrain=terrain, user=user, date=date, start_time=start, duration=dur)
                    r.full_clean(); r.save()
                    self.stdout.write(f'  ✅ Reservation: {terrain.name} on {date} at {start}')
                except Exception as e:
                    self.stdout.write(f'  ⚠️  Skipped: {e}')

        self.stdout.write(self.style.SUCCESS('\n🎉 Done! Accounts: admin/admin123, ayaka/pass1234, loli/pass1234'))
