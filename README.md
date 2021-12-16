django-easy-timezones
=====================

Easy IP-based timezones for Django based on **MaxMind GeoIP2** (see more: [Geolocation with GeoIP2 in Django](https://docs.djangoproject.com/en/3.2/ref/contrib/gis/geoip2/)) with IPv6 support.

> This repo is based on of django-easy-timezones (https://github.com/Miserlou/django-easy-timezones) with next fixes:
> 1. With using GeoIP2 instead of deprecated GeoIP.
> 2. Removed all databases from repo, so its size smaller and consists of only code without deprecated big-size databases (for this reason, this repository is not a fork and, accordingly, does not have the git historical data of the original repository)

Requirements:

- Python >= 3.5
- Django >= 2

Quick start
-----------


1. Install django-easy-timezones

    ```python
    pip install git+https://github.com/vivazzi/django-easy-timezones.git
    ```
   

2. Add `easy_timezones` to your `INSTALLED_APPS` setting like this:

    ```python
    INSTALLED_APPS = (
      ...
      'easy_timezones',
    )
    ```


3. Add `EasyTimezoneMiddleware` to your `MIDDLEWARE` 

    ```python
    MIDDLEWARE_CLASSES = (
      ...
      'easy_timezones.middleware.EasyTimezoneMiddleware',
    )
    ```
   

4. Download free databases from [maxmind.com](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) (requires sign up on the site).


5. Move downloaded databases to your project, for example, `/your_project/db/` and add `GEOIP_PATH` to your settings.py. `GEOIP_PATH` is path to directory with database files (`GeoLite2-City.mmdb` and `GeoLite2-Country.mmdb`).

    ```python
    GEOIP_PATH = PROJECT_DIR / 'db'
    ```
   
   If you have some projects, using common these city and country databases, you can use tha same `GEOIP_PATH` - no need to have multiple copies of databases in every project.


6. (Optionally) You can change default names of databases in `settings.py`:

    ```python
    GEOIP_COUNTRY = 'Custom-GeoLite2-City.mmdb'
    GEOIP_CITY = 'Custom-GeoLite2-Country.mmdb'
    ```

7. Enable localtime in your templates.

     ```python
     {% load tz %}
         The UTC time is {{ object.date }}
     {% localtime on %}
         The local time is {{ object.date }}
     {% endlocaltime %}
     ```

## Signals

You can also use signals to perform actions based on the timezone detection.

To hook into the Timezone detection event to, say, save it to the request's user somewhere more permanent than a session, do something like this:

```python
from easy_timezones.signals import detected_timezone	

@receiver(detected_timezone, sender=MyUserModel)
def process_timezone(sender, instance, timezone, **kwargs):
  if instance.timezone != timezone:
      instance.timezone = timezone
      instance.save()
```

## Customizing

Middleware in this package has a basic solution with the definition and activation of a timezone. 
In many real projects, the logic of work using the time zone is more complicated, 
so feel free to copy the middleware into your project and change for own needs.

For example, if it is required for authenticated users to use the timezone stored in the user model, then the middleware can be like this:

```python
from django.contrib.auth import get_user_model
from django.utils import timezone
from geoip2.errors import AddressNotFoundError

from easy_timezones.signals import detected_timezone
from easy_timezones.utils import geo_ip_2, get_ip_address_from_request, is_valid_ip, is_local_ip


class IPEasyTimezoneMiddleware:
    """
        Detect timezone from ip and save to cookie or user.timezone
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.timezone:
            tz = request.user.timezone
        else:
            tz = request.session.get('django_timezone')

        if not tz:
            # use the default timezone (settings.TIME_ZONE) for localhost
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

            if request.user.is_authenticated:
                if not request.user.timezone:
                    request.user.timezone = tz
                    request.user.save(update_fields=('timezone',))
            else:
                request.session['django_timezone'] = str(tz)

            if getattr(request, 'user', None) and request.user.is_authenticated:
                detected_timezone.send(sender=get_user_model(), instance=request.user, timezone=tz)
        else:
            timezone.deactivate()

        return self.get_response(request)
```

In this example, for anonymous users, the time zone will be saved in the session `request.session['django_timezone']`, 
and for authenticated users from `request.user.timezone`.

`user.timezone` in user model can be like this (requires `timezone_field` package):

```python
import pytz
from django.utils.translation import gettext_lazy as _
from timezone_field import TimeZoneField

class User(AbstractUser):
    TIMEZONE_CHOICES = [(pytz.timezone(tz), _(tz)) for tz in pytz.common_timezones]
    timezone = TimeZoneField(_('Time zone'), choices=TIMEZONE_CHOICES, blank=True)
```