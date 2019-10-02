import youtube_dl
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods


from .rabbit_connection import insert_in_queue


def home(request):
    return render(request, 'home.html')


@require_http_methods(['POST'])
def get(request):
    insert_in_queue(request.POST.get('url'))

    return redirect('home_page')