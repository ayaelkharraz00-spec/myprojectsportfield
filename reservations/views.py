"""
reservations/views.py  –  All page views (replacing the stub)
"""

import datetime
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages

from .models import Sport, Terrain, Reservation
from .forms import ReservationForm, UserRegisterForm, TerrainFilterForm


def home(request):
    context = {
        'total_sports':    Sport.objects.count(),
        'total_terrains':  Terrain.objects.count(),
        'available_count': Terrain.objects.filter(availability=True).count(),
        'sports':          Sport.objects.all(),
        'recent_reservations': Reservation.objects.select_related(
            'terrain', 'terrain__sport', 'user'
        ).order_by('-id')[:5],
    }
    return render(request, 'reservations/home.html', context)


def terrain_list(request):
    terrains = Terrain.objects.select_related('sport').all()
    form = TerrainFilterForm(request.GET or None)

    if form.is_valid():
        if form.cleaned_data.get('search'):
            terrains = terrains.filter(name__icontains=form.cleaned_data['search'])
        if form.cleaned_data.get('sport'):
            terrains = terrains.filter(sport=form.cleaned_data['sport'])
        av = form.cleaned_data.get('availability')
        if av == 'yes':
            terrains = terrains.filter(availability=True)
        elif av == 'no':
            terrains = terrains.filter(availability=False)

    return render(request, 'reservations/terrain_list.html', {
        'terrains': terrains, 'form': form, 'count': terrains.count()
    })


def terrain_detail(request, pk):
    terrain = get_object_or_404(Terrain.objects.select_related('sport'), pk=pk)
    today = datetime.date.today()
    upcoming = terrain.reservations.filter(date__gte=today).select_related('user').order_by('date', 'start_time')
    return render(request, 'reservations/terrain_detail.html', {
        'terrain': terrain, 'upcoming_reservations': upcoming, 'today': today
    })


@login_required
def make_reservation(request, terrain_pk):
    terrain = get_object_or_404(Terrain, pk=terrain_pk)

    if not terrain.availability:
        messages.error(request, f"{terrain.name} is not available for booking.")
        return redirect('terrain_detail', pk=terrain_pk)

    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user    = request.user
            reservation.terrain = terrain
            try:
                reservation.save()
                messages.success(request,
                    f"✅ Booking confirmed for {terrain.name} on "
                    f"{reservation.date} at {reservation.start_time.strftime('%H:%M')}!")
                return redirect('my_reservations')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = ReservationForm()

    return render(request, 'reservations/make_reservation.html', {'form': form, 'terrain': terrain})


def calendar_view(request):
    today = datetime.date.today()
    reservations = Reservation.objects.filter(date__gte=today).select_related(
        'terrain', 'terrain__sport', 'user'
    ).order_by('date', 'start_time')

    # Group by date
    grouped = {}
    for res in reservations:
        grouped.setdefault(res.date, []).append(res)

    return render(request, 'reservations/calendar.html', {
        'grouped_reservations': grouped,
        'total_upcoming': reservations.count(),
        'today': today,
    })


@login_required
def my_reservations(request):
    today = datetime.date.today()
    now   = datetime.datetime.now().time()
    all_res = Reservation.objects.filter(user=request.user).select_related(
        'terrain', 'terrain__sport'
    ).order_by('date', 'start_time')

    upcoming, past = [], []
    for res in all_res:
        if res.date > today or (res.date == today and res.start_time >= now):
            upcoming.append(res)
        else:
            past.append(res)

    return render(request, 'reservations/my_reservations.html', {
        'upcoming_reservations': upcoming, 'past_reservations': past
    })


@login_required
def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)
    if request.method == 'POST':
        name = reservation.terrain.name
        reservation.delete()
        messages.success(request, f"Reservation for {name} has been cancelled.")
        return redirect('my_reservations')
    return render(request, 'reservations/cancel_reservation.html', {'reservation': reservation})


# Edit a reservation
@login_required
def edit_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    today = datetime.date.today()
    now   = datetime.datetime.now().time()
    is_past = reservation.date < today or (
        reservation.date == today and reservation.start_time < now
    )
    if is_past:
        messages.error(request, "You cannot edit a reservation that has already passed.")
        return redirect('my_reservations')

    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            try:
                form.save()
                messages.success(
                    request,
                    f"✅ Reservation updated to {reservation.date} "
                    f"at {reservation.start_time.strftime('%H:%M')}!"
                )
                return redirect('my_reservations')
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = ReservationForm(instance=reservation)

    return render(request, 'reservations/edit_reservation.html', {
        'form':        form,
        'reservation': reservation,
        'terrain':     reservation.terrain,
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Account created.")
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'registration/register.html', {'form': form})