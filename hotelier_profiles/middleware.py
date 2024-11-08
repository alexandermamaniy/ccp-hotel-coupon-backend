# hotelier_profiles/middleware.py
from django.utils import timezone
from pytz import timezone as pytz_timezone
from django.utils.deprecation import MiddlewareMixin

class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile') and request.user.profile.timezone:
            user_timezone = request.user.profile.timezone
            timezone.activate(pytz_timezone(user_timezone))
        else:
            timezone.deactivate()
