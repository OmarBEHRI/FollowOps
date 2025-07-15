from django.shortcuts import render

def projects(request):
    return render(request, 'projects.html')


def projectDetails(request, pk):
    return render(request, 'projectDetails.html', {'pk': pk})

