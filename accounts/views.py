from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from django.urls import reverse_lazy
from django.views.generic import CreateView

from news_app.models import Category
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from .models import Profile
from django.core.exceptions import ObjectDoesNotExist



def user_login(request):
    global categories
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = authenticate(request,
                                username=data['username'],
                                password=data['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Login is successful!')
                else:
                    return HttpResponse('Your profile is not active')
            else:
                return HttpResponse('There is an error in the login or password')
    else:
        form = LoginForm()
        categories = Category.objects.all()
    context = {
        'form': form,
        'categories': categories

    }
    return render(request, 'registration/login.html', context)


# def dashboard_view(request):
#     user = request.user
#     profile_info = Profile.objects.filter(user=user)
#     categories = Category.objects.all()
#     context = {
#         'user': user,
#         'profile': profile_info,
#         'categories': categories
#     }
#     return render(request, 'pages/user_profile.html', context)

@login_required
def dashboard_view(request):
    user = request.user
    profile_info = user.profile
    categories = Category.objects.all()
    context = {
        'user': user,
        'profile': profile_info,
        'categories': categories
    }
    return render(request, 'pages/user_profile.html', context)



def user_register(request):
    if request.method == "POST":
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data["password"])
            categories = Category.objects.all()
            new_user.save()
            Profile.objects.create(user=new_user)
            context = {
                'new_user': new_user,
                'categories': categories
            }
            return render(request, 'account/register_done.html', context)
        else:
            # Return an error response if the form is not valid
            context = {
                'user_form': user_form
            }
            return render(request, 'account/register.html', context)
    else:
        user_form = UserRegistrationForm()
        categories = Category.objects.all()
        context = {
            'user_form': user_form,
            'categories': categories
        }
        return render(request, 'account/register.html', context)


# class SignUpView(CreateView):
#     form_class = UserCreationForm
#     success_url = reverse_lazy('login')
#     template_name = 'account/register.html'


    # def form_valid(self, form):
    #     response = super().form_valid(form)
    #     # Set the user's password after it's been created
    #     self.object.set_password(form.cleaned_data['password'])
    #     self.object.save()
    #     return response
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     categories = Category.objects.all()
    #     context['categories'] = categories
    #     return context





# def edit_user(request):
#     if request.method == 'POST':
#         user_form = UserEditForm(instance=request.user, data=request.POST)
#         profile_form = ProfileEditForm(instance=request.user.profile, data=request.POST, files=request.FILES)
#         if user_form.is_valid() and profile_form.is_valid():
#             user_form.save()
#             profile_form.save()
#     else:
#         user_form = UserEditForm(instance=request.user)
#         profile_form = ProfileEditForm(instance=request.user.profile)
#     return render(request, 'account/profile_edit.html', {"user_form": user_form, "profile_form": profile_form})



@login_required
def edit_user(request):
    try:
        profile = request.user.profile
    except ObjectDoesNotExist:
        profile = None

    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        if profile:
            profile_form = ProfileEditForm(instance=profile, data=request.POST, files=request.FILES)
        else:
            profile_form = ProfileEditForm(data=request.POST, files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            if profile:
                profile_form.save()
            else:
                new_profile = profile_form.save(commit=False)
                new_profile.user = request.user
                new_profile.save()
        return redirect('user_profile')
    else:
        user_form = UserEditForm(instance=request.user)
        if profile:
            profile_form = ProfileEditForm(instance=profile)
        else:
            profile_form = ProfileEditForm()
    return render(request, 'account/profile_edit.html', {"user_form": user_form, "profile_form": profile_form})

