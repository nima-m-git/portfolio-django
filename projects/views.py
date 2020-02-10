from django.shortcuts import render
from .models import Project
from django.http import HttpResponse

def project_index(request):
    '''Show all projects'''
    projects = Project.objects.all()
    context = {
        'projects': projects
    }
    return render(request, 'projects/project_index.html', context)


def project_detail(request, pk):
    '''Show details of a project'''
    project = Project.objects.get(pk=pk)
    context = {
        'project': project
    }
    return render(request, 'projects/project_detail.html', context)

