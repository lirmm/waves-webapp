from __future__ import unicode_literals
from braces.views import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views import generic
from waves.forms.profiles import UserForm, ProfileForm
from django.contrib.auth import logout
from base import WavesBaseContextMixin
import waves.models


class ShowProfile(LoginRequiredMixin, generic.TemplateView, WavesBaseContextMixin):
    template_name = "profiles/show_profile.html"
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        if slug:
            profile = get_object_or_404(waves.models.profiles.WavesProfile, slug=slug)
            user = profile.user
        else:
            user = self.request.user

        if user == self.request.user:
            kwargs["editable"] = True
        kwargs["show_user"] = user
        return super(ShowProfile, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = self.request.user
        if user:
            user.delete()
        return redirect("home")


class EditProfile(LoginRequiredMixin, generic.TemplateView, WavesBaseContextMixin):
    template_name = "profiles/edit_profile.html"
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):
        user = self.request.user
        if "user_form" not in kwargs:
            kwargs["user_form"] = UserForm(instance=user)
        if "profile_form" not in kwargs:
            kwargs["profile_form"] = ProfileForm(instance=user.profile)
        return super(EditProfile, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if request.POST.get('delete_profile'):
            user = self.request.user
            user.delete()
            logout(request)
            messages.success(request, 'Your profile has been deleted !')
            return redirect('waves:home')
        user = self.request.user
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST,
                                   request.FILES,
                                   instance=user.profile)
        if not (user_form.is_valid() and profile_form.is_valid()):
            messages.error(request, "There was a problem with the form. "
                                    "Please check the details.")
            user_form = UserForm(instance=user)
            profile_form = ProfileForm(instance=user.profile)
            return super(EditProfile, self).get(request,
                                                user_form=user_form,
                                                profile_form=profile_form)
        # Both forms are fine. Time to save!
        user_form.save()
        profile = profile_form.save(commit=False)
        profile.user = user
        profile.save()
        messages.success(request, "Profile details saved!")
        return redirect("waves:show_self")
