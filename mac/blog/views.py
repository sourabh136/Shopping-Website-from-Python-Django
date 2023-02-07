from django.shortcuts import render
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
# Create your views here.

def index(request):
    nblogs=Blogpost.objects.all()
    # print(nblogs)
    # return render(request,'blog/index.html',{'nblogs':n_blogs})

    return render(request,'blog/index.html',{"nblogs":nblogs})

def blogpost(request,id):
    post=Blogpost.objects.filter(post_id=id)[0]
    # print(post.title,post.chead0)
    # n_blogs=Blogpost.objects.all()
    # return render(request,'blog/blogpost.html',{'nblogs':n_blogs})
    return render(request,'blog/blogpost.html',{"post":post})
   
#shop ki appp ka kaam yaha karna hai
