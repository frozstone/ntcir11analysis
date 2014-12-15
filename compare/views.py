from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from os import path, getcwd

# Create your views here.
def index(request):
    queries = [{'title':'FT-20', 'maths':[{'tex':'\sqrt{3}'}]}]
    template = loader.get_template('index.html')
    context = RequestContext(request, {'queries':queries,})
    return HttpResponse(template.render(context))
