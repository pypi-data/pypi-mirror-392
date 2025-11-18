from debconf.common_settings import *

INSTALLED_APPS = (
    'badges',
    'daytrip',
    'debconf',
    'exports',
    'bursary',
    'front_desk',
    'invoices',
    'register',
) + INSTALLED_APPS

BAKERY_VIEWS += (
    'register.views.statistics.StatisticsView',
)

WAFER_USER_CHECKED_IN = 'frontdesk.models.is_checked_in'
