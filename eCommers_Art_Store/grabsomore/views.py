import secrets
from datetime import timedelta
from hashlib import sha1

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone

from .models import ResetToken


def home(request):
    """Public landing page explaining what ArtisanHub is, shown
    before anyone logs in."""

    return render(request, 'grabsomore/home.html')


def login_user(request):
    """Log a user in and redirect them to the welcome page."""

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Check if the username and password match a user in the DB
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)  # Log the user in and start their session

            # Keep the session alive for 30 days instead of expiring
            # it as soon as the browser closes.
            request.session.set_expiry(timedelta(days=30))

            # Save some user info in the session (optional, but useful)
            request.session['user_id'] = user.id
            request.session['username'] = user.username

            # Redirect user to the welcome page after successful login
            return HttpResponseRedirect(reverse('grabsomore:welcome'))
        else:
            # If login failed, reload login page with an error message
            return render(request, 'grabsomore/login.html', {
                'error': 'Invalid credentials'
            })

    # If the user just opened the login page, show the login form
    return render(request, 'grabsomore/login.html')


def register_user(request):
    """Handle user registration (signing up)."""

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        password_conf = request.POST.get('password_conf')
        email = request.POST.get('email')
        account_type = request.POST.get('account_type')

        if password != password_conf:
            return render(request, 'grabsomore/register.html', {
                'error': 'Passwords do not match.'
            })

        if User.objects.filter(username=username).exists():
            return render(request, 'grabsomore/register.html', {
                'error': 'That username is already taken.'
            })

        if User.objects.filter(email=email).exists():
            return render(request, 'grabsomore/register.html', {
                'error': 'That email is already registered.'
            })

        try:
            validate_password(password)
        except ValidationError as e:
            return render(request, 'grabsomore/register.html', {
                'error': ' '.join(e.messages)
            })

        user = User.objects.create_user(
            username=username, password=password, email=email
        )

        group_name = 'Vendors' if account_type == 'vendor' else 'Buyers'
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
        except Group.DoesNotExist:
            pass

        login(request, user)
        return redirect(reverse('grabsomore:welcome'))

    return render(request, 'grabsomore/register.html')


def logout_user(request):
    """Log the current user out, if they were logged in, and send
    them back to the login page."""

    if request.user.is_authenticated:
        logout(request)
    return HttpResponseRedirect(reverse('grabsomore:login'))


@login_required(login_url=reverse_lazy('grabsomore:login'))
def welcome(request):
    """Show the welcome page. Only logged-in users can see it."""

    return render(request, 'grabsomore/welcome.html')


def build_email(user, reset_url):
    """Build the password reset email for a user."""

    subject = "Password Reset"
    # The "from" address for the email
    domain_email = "example@domain.com"
    body = (
        f"Hi {user.username},\n"
        f"Here is your link to reset your password: {reset_url}"
    )

    return EmailMessage(subject, body, domain_email, [user.email])


def generate_reset_url(request, user):
    """Create a single-use, 5-minute reset token for the user and
    return the absolute URL they should visit to use it."""

    token = secrets.token_urlsafe(16)  # Random, high-entropy token
    expiry_date = timezone.now() + timedelta(minutes=5)
    # Store only the hash, never the raw token
    hashed_token = sha1(token.encode()).hexdigest()

    ResetToken.objects.create(
        user=user, token=hashed_token, expiry_date=expiry_date
    )

    path = reverse('grabsomore:password_reset_form', args=[token])
    return request.build_absolute_uri(path)


def send_password_reset(request):
    """Email a password reset link to the address the user submits."""

    if request.method == 'POST':
        user_email = request.POST.get('email')
        try:
            user = User.objects.get(email=user_email)
            reset_url = generate_reset_url(request, user)
            email = build_email(user, reset_url)
            email.send()
        except ObjectDoesNotExist:
            # Even if no user is found, do nothing here and still show
            # the confirmation below (to avoid leaking which emails
            # are registered).
            pass

        return render(request, 'grabsomore/reset_email_sent.html', {
            'email': user_email
        })

    # Show the form where user can enter their email
    return render(request, 'grabsomore/request_password_reset.html')


def reset_user_password(request, token):
    """Validate a reset token from the email link and show the form
    to enter a new password."""

    hashed_token = sha1(token.encode()).hexdigest()  # Hash token from URL

    try:
        user_token = ResetToken.objects.get(token=hashed_token)

        if user_token.expiry_date < timezone.now():
            user_token.delete()  # Delete expired token
            return render(
                request, 'grabsomore/password_reset_expired.html'
            )

        # Save user ID and token in session to verify the next step
        request.session['user_id'] = user_token.user.id
        request.session['reset_token'] = token

        return render(request, 'grabsomore/password_reset.html', {
            'token': token
        })

    except ResetToken.DoesNotExist:
        # Token not found
        return render(request, 'grabsomore/password_reset_invalid.html')


def reset_password(request):
    """Handle the form submission that actually changes the password."""

    if request.method != 'POST':
        return HttpResponseRedirect(reverse('grabsomore:login'))

    user_id = request.session.get('user_id')
    token = request.session.get('reset_token')
    password = request.POST.get('password')
    password_conf = request.POST.get('password_conf')

    # Check if all required data is present
    if not all([user_id, token, password, password_conf]):
        return render(request, 'grabsomore/password_reset.html', {
            'error': 'Missing fields or session expired.',
            'token': token,
        })

    # Check if passwords match
    if password != password_conf:
        return render(request, 'grabsomore/password_reset.html', {
            'error': 'Passwords do not match.',
            'token': token,
        })

    try:
        user = User.objects.get(id=user_id)
        hashed_token = sha1(token.encode()).hexdigest()
        reset_token = ResetToken.objects.get(token=hashed_token, user=user)

        # Check token expiry again (just to be sure)
        if reset_token.expiry_date < timezone.now():
            reset_token.delete()
            return render(
                request, 'grabsomore/password_reset_expired.html'
            )

        # Update the user's password (hashed securely)
        user.password = make_password(password)
        user.save()

        # Delete the token and clear session info
        reset_token.delete()
        request.session.flush()

        # Redirect user to login page after successful password reset
        return HttpResponseRedirect(reverse('grabsomore:login'))

    except (User.DoesNotExist, ResetToken.DoesNotExist):
        return render(request, 'grabsomore/password_reset_invalid.html')
