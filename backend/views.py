from django.shortcuts import render

def home(request):
    """Render a simple Django template at the root URL."""
    return render(request, 'index.html')
