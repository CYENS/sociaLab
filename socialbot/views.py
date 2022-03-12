from django.http import HttpResponse
import subprocess



def index(request):
    return HttpResponse("Hello, world2")


def autodeploy(request):
    result = subprocess.run(["sudo","-u","christosmichael","sh", "autodeploy.sh"], stderr=subprocess.PIPE)
    return HttpResponse(result.stderr)
