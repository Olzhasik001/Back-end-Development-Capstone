import os
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.hashers import make_password

from concert.forms import LoginForm, SignUpForm
from concert.models import Concert, ConcertAttending
import requests as req

SONGS_URL = os.environ.get("SONGS_URL", "http://localhost:5000")
PICTURES_URL = os.environ.get("PICTURES_URL", "http://localhost:5001")
# Create your views here.

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if User.objects.filter(username=username).exists():
            return render(request, "signup.html", {"form": SignUpForm, "message": "user already exist"})
        user = User.objects.create(username=username, password=make_password(password))
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    return render(request, "signup.html", {"form": SignUpForm})


def index(request):
    return render(request, "index.html")


def songs(request):
    data = req.get(SONGS_URL + "/song").json()
    song_list = data["songs"] if isinstance(data, dict) else data
    return render(request, "songs.html", {"songs": song_list})


def photos(request):
    photos = req.get(PICTURES_URL + "/picture").json()
    return render(request, "photos.html", {"photos": photos})
    
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        return render(request, "login.html", {"form": LoginForm, "message": "Invalid username or password"})
    return render(request, "login.html", {"form": LoginForm})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


def concerts(request):
    concert_list = Concert.objects.all()
    return render(request, "concerts.html", {"concerts": concert_list})


def concert_detail(request, id):
    if request.user.is_authenticated:
        obj = Concert.objects.get(pk=id)
        try:
            status = obj.attendee.filter(user=request.user).first().attending
        except:
            status = "-"
        return render(request, "concert_detail.html", {"concert_details": obj, "status": status, "attending_choices": ConcertAttending.AttendingChoices.choices})
    else:
        return HttpResponseRedirect(reverse("login"))
    pass


def concert_attendee(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            concert_id = request.POST.get("concert_id")
            attendee_status = request.POST.get("attendee_choice")
            concert_attendee_object = ConcertAttending.objects.filter(
                concert_id=concert_id, user=request.user).first()
            if concert_attendee_object:
                concert_attendee_object.attending = attendee_status
                concert_attendee_object.save()
            else:
                ConcertAttending.objects.create(concert_id=concert_id,
                                                user=request.user,
                                                attending=attendee_status)

        return HttpResponseRedirect(reverse("concerts"))
    else:
        return HttpResponseRedirect(reverse("index"))
