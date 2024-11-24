from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView

from maingame.models import Dominion, Event, UserSettings, Theme


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        new_user = User.objects.get(username=form.cleaned_data["username"])
        open_dominion_theme = Theme.objects.get(name="OpenDominion")
        UserSettings.objects.create(associated_user=new_user, display_name=new_user.username, theme_model=open_dominion_theme)
        
        return response