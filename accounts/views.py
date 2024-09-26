from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.views.generic import CreateView

from maingame.models import Player, Event


class SignUpView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        new_user = User.objects.get(username=form.cleaned_data["username"])
        Player.objects.create(associated_user=new_user, name="Erik forgot a round signup process")
        
        return response