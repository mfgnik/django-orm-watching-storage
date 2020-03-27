import datetime


from datacenter.models import Passcard
from datacenter.models import Visit
from django.shortcuts import render
from django.utils.timezone import localtime, now


HOUR = 3600


def get_duration(visit):
    if visit.leaved_at is None:
        visit_end = now()
    else:
        visit_end = localtime(visit.leaved_at)
    return int((visit_end - localtime(visit.entered_at)).total_seconds())


def format_duration(duration):
    hours, minutes, seconds = duration // 3600, duration // 60 % 60, duration % 60
    if hours:
        return f'{hours:d}:{minutes:02d}:{seconds:02d}'
    return f'{minutes:d}:{seconds:02d}'


def local_and_format_time(visit):
    return localtime(visit.entered_at).strftime("%d-%m-%Y %H:%M")


def is_visit_long(duration):
    return duration > HOUR


def is_person_suspicious(visits):
    for visit in visits:
        if is_visit_long(get_duration(visit)):
            return True
    return False


def get_all_visits_of_visitor(visit):
    return Visit.objects.filter(passcard__owner_name=visit.passcard.owner_name)


def get_visit_dict(visit):
    return {
      "who_entered": visit.passcard.owner_name,
      "entered_at": local_and_format_time(visit),
      "duration": format_duration(get_duration(visit)),
      "is_strange": "Yes" if is_person_suspicious(get_all_visits_of_visitor(visit)) else "No",
      }


def storage_information_view(request):
    non_closed_visits = [
      get_visit_dict(visit) for visit in  Visit.objects.filter(leaved_at=None)
      ]
    context = {
        "non_closed_visits": non_closed_visits,
    }
    return render(request, 'storage_information.html', context)
