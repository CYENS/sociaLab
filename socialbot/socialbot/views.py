from django.http import HttpResponse
import subprocess



def index(request):
    return HttpResponse("Hello, world3.2")


def autodeploy(request):
    result = subprocess.run(["sh", "autodeploy.sh"], stderr=subprocess.PIPE)
    return HttpResponse(result.stderr)
