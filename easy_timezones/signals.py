import django.dispatch

detected_timezone = django.dispatch.Signal(['instance', 'timezone'])
