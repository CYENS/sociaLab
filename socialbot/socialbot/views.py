from django.http import HttpResponse
from django.shortcuts import render
import subprocess



def index(request):
    return HttpResponse("Hello, world3.3")


def autodeploy(request):
    result = subprocess.run(["sh", "autodeploy.sh"], stderr=subprocess.PIPE)
    return HttpResponse(result.stderr)

def privacy (request):
    return render(request, 'templates/privacy.html')
