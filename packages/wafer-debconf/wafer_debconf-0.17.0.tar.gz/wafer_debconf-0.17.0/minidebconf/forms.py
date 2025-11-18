from datetime import timedelta
from django import forms
from django.conf import settings
from django.utils import formats
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext_lazy as _p

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, HTML

from minidebconf.models import Diet, Registration, RegistrationType, ShirtSize
from minidebconf.models import ScheduleBlock


def format_day(day):
    date = formats.date_format(day, format="SHORT_DATE_FORMAT")
    weekday = formats.date_format(day, format="l")
    return f"{date} ({weekday})"


def attendance_days():
    days = ScheduleBlock.objects.order_by("start_time")
    return [(day.pk, format_day(day.start_time)) for day in days]


def select_check_in_check_out():
    dates = [d.start_time.date() for d in ScheduleBlock.objects.order_by("start_time")]
    one_day = timedelta(days=1)
    dates.insert(0, dates[0] - one_day)
    dates.append(dates[-1] + one_day)
    return [(date, format_day(date)) for date in dates]


def register_form_factory():
    form_fields = ['full_name']
    if settings.MINIDEBCONF_REGISTER_PHONE is not None:
        form_fields.append('phone_number')
    if RegistrationType.objects.exists():
        form_fields.append('registration_type')
    form_fields.append('full_name')
    form_fields.append('involvement')
    form_fields.append('gender')
    form_fields.append('country')
    form_fields.append('city_state')
    if ScheduleBlock.objects.count() > 0:
        form_fields.append('days')
    if settings.MINIDEBCONF_REGISTER_ARRANGED_ACCOMMODATION:
        form_fields.append('arranged_accommodation')
        form_fields.append("check_in")
        form_fields.append("check_out")
    if settings.MINIDEBCONF_REGISTER_ARRANGED_FOOD:
        form_fields.append('arranged_food')
    if Diet.objects.exists():
        form_fields.append('diet')
    if settings.MINIDEBCONF_REGISTER_TRAVEL_REIMBURSEMENT:
        form_fields.append("travel_reimbursement")
        form_fields.append("travel_cost")
    if ShirtSize.objects.exists():
        form_fields.append('shirt_size')
    form_fields.append("notes")
    form_fields.append("openpgp_fingerprint")


    class RegisterForm(forms.ModelForm):
        full_name = forms.CharField(max_length=256, label=_('Full name'))
        class Meta:
            model = Registration
            fields = form_fields
            widgets = {
                'days': forms.CheckboxSelectMultiple(),
                'check_in': forms.Select(),
                'check_out': forms.Select(),
            }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.fields["full_name"].initial = self.instance.full_name
            if 'days' in self.fields:
                self.fields["days"].choices = attendance_days()
            if 'phone_number' in self.fields:
                self.fields["phone_number"].required = settings.MINIDEBCONF_REGISTER_PHONE
            if settings.MINIDEBCONF_REGISTER_DEFAULT_COUNTRY:
                self.initial['country'] = settings.MINIDEBCONF_REGISTER_DEFAULT_COUNTRY
            if 'arranged_accommodation' in self.fields:
                self.fields['arranged_accommodation'].label = _('I would like to stay at the conference-arranged accommodation')
            if 'arranged_food' in self.fields:
                self.fields['arranged_food'].label = _('I would like to have the conference-arranged meals')
            if 'travel_reimbursement' in self.fields:
                self.fields["travel_reimbursement"].label = _('I would like to request reimbursement of my travel costs')
            if 'travel_cost' in self.fields:
                self.fields['travel_cost'].label = _('Estimated travel cost (upper bound, in %(currency)s)') % { 'currency': settings.DEBCONF_BURSARY_CURRENCY_SYMBOL }

            self.helper = FormHelper()

            layout = [
                'full_name',
                'phone_number',
                'involvement',
                'gender',
                'country',
                'city_state',
                'days',
            ]
            if 'shirt_size' in self.fields:
                if page := settings.MINIDEBCONF_REGISTER_SHIRT_INFO_PAGE:
                    info = [HTML(_("<p><a href='%s' target='_blank'>See this page</a> for more information about shirt sizes.</p>") % page)]
                else:
                    info = []
                layout += [
                    Fieldset(
                        _('T-Shirt'),
                        *info,
                        'shirt_size',
                    )
                ]
            if 'arranged_food' in self.fields or 'arranged_accommodation' in self.fields or 'travel_reimbursement' in self.fields:
                accommodation_dates = select_check_in_check_out()
                if 'check_in' in self.fields:
                    self.fields['check_in'].widget.choices = accommodation_dates
                    self.fields['check_in'].initial = accommodation_dates[0][0]
                if 'check_out' in self.fields:
                    self.fields['check_out'].widget.choices = accommodation_dates
                    self.fields['check_out'].initial = accommodation_dates[-1][0]

                if page := settings.MINIDEBCONF_REGISTER_BURSARY_INFO_PAGE:
                    info = [HTML(_("<p><a href='%s' target='_blank'>See this page</a> for more information about bursaries.</p>") % page)]
                else:
                    info = []
                diet = ('diet' in self.fields) and ['diet'] or []
                food = ('arranged_food' in self.fields) and ['arranged_food'] or []


                layout += [
                    Fieldset(
                        _('Bursaries'),
                        *info,
                        *food,
                        *diet,
                        'arranged_accommodation',
                        'check_in',
                        'check_out',
                        'travel_reimbursement',
                        'travel_cost',
                        id='bursary_fields',
                    )
                ]

            layout += ['notes']
            layout += ['openpgp_fingerprint']

            if self.instance.id:
                submit = _p("conference", "Update registration")
            else:
                submit = _p("conference", "Register")
            layout += [Submit("submit", submit)]
            self.helper.layout = Layout(*layout)


        def save(self):
            super().save()
            name = self.cleaned_data['full_name'].split()
            user = self.instance.user
            user.first_name = name[0]
            user.last_name = " ".join(name[1:])
            user.save()
    return RegisterForm
