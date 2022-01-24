from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegisterForm
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib import messages
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.views.generic import UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

User = get_user_model()


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            token = PasswordResetTokenGenerator().make_token(user)
            message = render_to_string('acc_activate_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uidb64': user.pk,
                'token': token,
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            messages.info(request, 'Please check your email to confirm your account!')
            return redirect('/')
    else:
        form = RegisterForm()
    args = {'form': form}
    return render(request, 'user/register.html', args)


def activate(request, uidb64, token):
    try:
        uid = uidb64
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and PasswordResetTokenGenerator().check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.info(request, 'Thank you for your email confirmation.')
        return redirect('/')
    else:
        return HttpResponse('Activation link is invalid!')


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'profile_photo', 'phone', 'email']
    template_name = 'user/user_update.html'
    login_url = 'login'
    username = 'username'


def profile_view(request):
    return render(request, 'user/profile.html')
