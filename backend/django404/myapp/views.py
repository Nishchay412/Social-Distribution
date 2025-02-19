from django.http import HttpResponse

def home(request):
    return HttpResponse("Hello, Django!")


# view to recieve data from the frontend and then send it to the serializer so it can convert 
# to the python object . 




