from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


@login_required
def dashboard_view(request):
    """Redirect /dashboard/ to the main user dashboard UI."""
    return redirect('home')