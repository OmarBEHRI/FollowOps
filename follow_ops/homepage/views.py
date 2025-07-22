from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import ensure_csrf_cookie
import json

# Create your views here.
@ensure_csrf_cookie
def homepage(request):
    return render(request, 'index.html')

def login_view(request):
    if request.method == 'POST':
        try:
            if request.headers.get('Content-Type') == 'application/json':
                data = json.loads(request.body)
                email = data.get('email')
                password = data.get('password')
            else:
                email = request.POST.get('email')
                password = request.POST.get('password')
                
            user = authenticate(request, username=email, password=password)
            
            if user is not None:
                login(request, user)
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'success': True})
                return redirect('/dashboard/')
            else:
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'error': 'Identifiants invalides'}, status=400)
                return render(request, 'index.html', {'error': 'Identifiants invalides'})
        except Exception as e:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'error': str(e)}, status=400)
            return render(request, 'index.html', {'error': str(e)})
    
    return redirect('/')
