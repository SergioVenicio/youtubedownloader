import youtube_dl
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods


def home(request):
    return render(request, 'home.html')


@require_http_methods(['POST'])
def get(request):
    options = {
        'outtmpl': '/videos/%(title)s.%(ext)s',
    }

    # TODO - create downloader QUEUE

    with youtube_dl.YoutubeDL(options) as ydl:
        response = ydl.extract_info(request.POST.get('url'), download=True)

        print(response)

    return redirect('home_page')
