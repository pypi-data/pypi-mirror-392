from django.conf import settings

def expose_settings(request):
    return {
        'MINIDEBCONF_REGISTER_BURSARY_CONTRIBUTORS_ONLY': getattr(settings, "MINIDEBCONF_REGISTER_BURSARY_CONTRIBUTORS_ONLY", False),
    }
