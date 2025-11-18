from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.utils.functional import SimpleLazyObject

from timezone.models import Timezone


def get_timezone(request):
    if not hasattr(request, "_cached_timezone"):
        if not request.user.is_authenticated:
            timezone.deactivate()
            request._cached_timezone = None
        else:
            tz, created = Timezone.objects.get_or_create(owner=request.user)
            timezone.activate(tz.timezone)
            request._cached_timezone = tz

    return request._cached_timezone


class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.timezone = SimpleLazyObject(lambda: get_timezone(request))

    def process_response(self, request, response):
        if hasattr(request, "_cached_timezone"):
            response["X-Timezone"] = request._cached_timezone
        return response
