from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import ImageFeed
from .utils import process_image
from .forms import ImageFeedForm
from django.views.generic import TemplateView


class home(TemplateView):
    template_name = 'object_detection/home.html'


class register(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = UserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
                login(request, user)
                return redirect('object_detection:dashboard')
        else:
            form = UserCreationForm()
        return render(request, 'object_detection/register.html', {'form': form})


class user_login(TemplateView):
    def get(self, request, *args, **kwargs):
        if request.method == 'POST':
            form = AuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                return redirect('object_detection:dashboard')
        else:
            form = AuthenticationForm()
        return render(request, 'object_detection/login.html', {'form': form})


class user_logout(TemplateView):
    @login_required
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('object_detection:login')

class dashboard(TemplateView):
    @login_required
    def get(self, request, *args, **kwargs):
        image_feeds = ImageFeed.objects.filter(user=request.user)
        return render(request, 'object_detection/dashboard.html', {'image_feeds': image_feeds})


@login_required
def process_image_feed(request, feed_id):
    image_feed = get_object_or_404(ImageFeed, id=feed_id, user=request.user)
    process_image(feed_id)  # Consider handling this asynchronously
    return redirect('object_detection:dashboard')


@login_required
def add_image_feed(request):
    if request.method == 'POST':
        form = ImageFeedForm(request.POST, request.FILES)
        if form.is_valid():
            image_feed = form.save(commit=False)
            image_feed.user = request.user
            image_feed.save()
            return redirect('object_detection:dashboard')
    else:
        form = ImageFeedForm()
    return render(request, 'object_detection/add_image_feed.html', {'form': form})


@login_required
def delete_image(request, image_id):
    image = get_object_or_404(ImageFeed, id=image_id, user=request.user)  # Ensuring only the owner can delete
    image.delete()
    return redirect('object_detection:dashboard')
