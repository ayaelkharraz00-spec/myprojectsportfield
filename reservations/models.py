

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import timedelta, datetime


class Sport(models.Model):
    name         = models.CharField(max_length=100)
    max_capacity = models.IntegerField()

    # Map sport names to Bootstrap Icons class names (used in templates)
    SPORT_ICONS = {
        'Football': 'bi-dribbble', 'Tennis': 'bi-trophy',
        'Basketball': 'bi-circle', 'Padel': 'bi-grid',
        'Volleyball': 'bi-circle-half', 'Rugby': 'bi-shield',
    }

    def get_icon(self):
        return self.SPORT_ICONS.get(self.name, 'bi-lightning')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Terrain(models.Model):
    SURFACE_CHOICES = [
        ('gazon',        'Gazon (Natural Grass)'),
        ('synthetique',  'Synthétique'),
        ('parquet',      'Parquet'),
        ('terre_battue', 'Terre battue (Clay)'),
    ]
    SURFACE_EMOJIS = {
        'gazon': '🌿', 'synthetique': '🟩',
        'parquet': '🪵', 'terre_battue': '🟤',
    }

    name          = models.CharField(max_length=100)
    surface_type  = models.CharField(max_length=20, choices=SURFACE_CHOICES)
    availability  = models.BooleanField(default=True)
    sport         = models.ForeignKey(Sport, on_delete=models.CASCADE, related_name='terrains')

    def get_surface_emoji(self):
        return self.SURFACE_EMOJIS.get(self.surface_type, '🏟️')

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Reservation(models.Model):
    terrain    = models.ForeignKey(Terrain, on_delete=models.CASCADE, related_name='reservations')
    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations')
    date       = models.DateField()
    start_time = models.TimeField()
    duration   = models.IntegerField(help_text="Duration in hours")
    created_at = models.DateTimeField(auto_now_add=True, null=True)

    def get_end_time(self):
        start_dt = datetime.combine(self.date, self.start_time)
        return (start_dt + timedelta(hours=self.duration)).time()

    def clean(self):
        #Prevention de  overlapping rser
        if not all([self.terrain_id, self.date, self.start_time, self.duration]):
            return

        start_dt = datetime.combine(self.date, self.start_time)
        end_dt   = start_dt + timedelta(hours=self.duration)

        # Past date guard
        import datetime as dt
        if self.date < dt.date.today():
            raise ValidationError("You cannot make a reservation in the past.")

        # Overlap check
        others = Reservation.objects.filter(terrain=self.terrain, date=self.date).exclude(id=self.id)
        for res in others:
            ex_start = datetime.combine(res.date, res.start_time)
            ex_end   = ex_start + timedelta(hours=res.duration)
            if start_dt < ex_end and end_dt > ex_start:
                raise ValidationError(
                    f"This field is already booked from "
                    f"{res.start_time.strftime('%H:%M')} to {ex_end.strftime('%H:%M')}. "
                    f"Please choose a different time."
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.terrain.name} – {self.date} {self.start_time}"

