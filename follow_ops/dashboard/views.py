from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def dashboard(request):
    # Get the current user
    user = request.user
    
    # Determine which dashboard template to render based on user's role
    if user.appRole == 'ADMIN':
        return render(request, 'dashboard.html')  # Admin dashboard (original)
    elif user.appRole == 'MANAGER':
        return render(request, 'dashboard_manager.html')  # Manager dashboard
    else:  # USER role
        return render(request, 'dashboard_user.html')  # User dashboard