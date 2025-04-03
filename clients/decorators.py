from functools import wraps
from django.shortcuts import get_object_or_404
from django.http import HttpResponseForbidden
from .models import Client, Staff
from django.shortcuts import redirect

def dynamic_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Extract the slug from the URL parameters
        slug = kwargs.get('slug', '')
        if not request.user.is_authenticated:
            # Redirect to the login URL with the dynamic slug
            return redirect(f'/{slug}/login/?next={request.path}')
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def team_member_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, slug, *args, **kwargs):
        client = Client.objects.filter(slug=slug).first()
        is_team_member = Staff.objects.filter(client=client, user=request.user).exists()
        if not is_team_member:
            return HttpResponseForbidden("You do not have permission to visit this page.")
        return view_func(request, slug, *args, **kwargs)
    return _wrapped_view
