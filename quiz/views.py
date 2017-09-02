"""Quiz views"""
from django.shortcuts import render


def index(request):
    """Humble index view"""
    context = {
        'display_text': 'Welcome to Radical Quiz! '
                        'Feel free to click the buttons above!'
    }
    return render(request, 'index.html', context)
