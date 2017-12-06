# Create your views here.
from clamopener import settings
from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {'services': settings.SERVICES})
