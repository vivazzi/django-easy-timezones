from django.contrib.auth import get_user_model

from easy_timezones.signals import detected_timezone

from django.utils import timezone
from geoip2.errors import AddressNotFoundError

from easy_timezones.utils import geo_ip_2, get_ip_address_from_request, is_valid_ip, is_local_ip


class EasyTimezoneMiddleware:
    """
        Detect timezone from ip and save to cookie. After we can save timezone when user has registered
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tz = request.session.get('django_timezone')

        if not tz:
            tz = timezone.get_default_timezone()

            client_ip = get_ip_address_from_request(request)
            ip_addrs = client_ip.split(',')
            for ip in ip_addrs:
                if is_valid_ip(ip) and not is_local_ip(ip):
                    try:
                        tz = geo_ip_2.city(ip)['time_zone']
                    except AddressNotFoundError:
                        pass

                    break

        if tz:
            timezone.activate(tz)
            request.session['django_timezone'] = str(tz)
            if getattr(request, 'user', None) and request.user.is_authenticated:
                detected_timezone.send(sender=get_user_model(), instance=request.user, timezone=tz)
        else:
            timezone.deactivate()

        return self.get_response(request)
