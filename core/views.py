from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from rabbit import queues


def home(request):
    return render(request, 'home.html')


@require_http_methods(['POST'])
def get(request):
    video_publisher = queues.VideoQueue()
    video_publisher.exchange_declare()
    video_publisher.queue_declare()
    video_publisher.queue_bind()
    video_publisher.publish_msg(request.POST.get('url'))

    return redirect('home_page')
