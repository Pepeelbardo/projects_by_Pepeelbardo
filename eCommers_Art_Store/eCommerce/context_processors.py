def user_role(request):
    """Expose the current user's vendor/buyer status to every template,
    so the shared navigation bar can show only role-appropriate links."""

    is_vendor = False
    if request.user.is_authenticated:
        is_vendor = request.user.groups.filter(name='Vendors').exists()

    return {
        'is_vendor': is_vendor,
    }
