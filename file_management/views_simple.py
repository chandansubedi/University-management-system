from django.http import HttpResponse

def hello_upload(request):
    return HttpResponse("Hello! Upload Files page is working! 🎉")

def hello_files(request):
    return HttpResponse("Hello! My Files page is working! 🎉")

def hello_student_files(request):
    return HttpResponse("Hello! Student Files page is working! 🎉")
