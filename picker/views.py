from django.shortcuts import render, render_to_response
from django.contrib.auth import logout, login, authenticate, get_user_model
from django.template import RequestContext
from django.contrib.auth.forms import AuthenticationForm
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseNotFound

from picker.models import *

# overview page. 
@csrf_protect
def overview(request, **kwargs):
    login_form = AuthenticationForm()
    weekly_chores = ScheduledChore.objects.filter(chore__frequency = 'weekly', done = False)
    sun_chores = ScheduledChore.objects.filter(chore__frequency = 'daily', done = False, day = 0)
    mon_chores = ScheduledChore.objects.filter(chore__frequency = 'daily', done = False, day = 1)
    tue_chores = ScheduledChore.objects.filter(chore__frequency = 'daily', done = False, day = 2)
    wed_chores = ScheduledChore.objects.filter(chore__frequency = 'daily', done = False, day = 3)
    thu_chores = ScheduledChore.objects.filter(chore__frequency = 'daily', done = False, day = 4)
    fri_chores = ScheduledChore.objects.filter(chore__frequency = 'daily', done = False, day = 5)
    sat_chores = ScheduledChore.objects.filter(chore__frequency = 'daily', done = False, day = 6)
    return render(request, 
                  'overview.html', 
                   {'weekly_chores':weekly_chores,
                    'sun_chores':sun_chores,
                    'mon_chores':mon_chores,
                    'tue_chores':tue_chores,
                    'wed_chores':wed_chores,
                    'thu_chores':thu_chores,
                    'fri_chores':fri_chores,
                    'sat_chores':sat_chores,
                    'sun_rows':len(sun_chores)+1,
                    'mon_rows':len(mon_chores)+1,
                    'tue_rows':len(tue_chores)+1,
                    'wed_rows':len(wed_chores)+1,
                    'thu_rows':len(thu_chores)+1,
                    'fri_rows':len(fri_chores)+1,
                    'sat_rows':len(sat_chores)+1,
                    'login_form':login_form,
                    'user':request.user})

# sign the user in.
@csrf_protect
def signin(request, *args, **kwargs):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                login(request, user)
                return HttpResponseRedirect('/')

    else:
        form = AuthenticationForm()
    variables = RequestContext(request, {'form':form})
    return render_to_response('login.html', variables)

# log the user out.
def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')

def done(request, **kwargs):
    if request.method != 'POST':
        return HttpResponseNotFound()
    scheduledChore = ScheduledChore.objects.get(pk=kwargs['sc_id'])
    if request.user != scheduledChore.person:
        return HttpResponseNotFound()
    scheduledChore.done = True
    scheduledChore.save()
    return HttpResponseRedirect('/')

def give_away_weekly(request, **kwargs):
    if request.method != 'POST':
        return HttpResponseNotFound()
    scheduledChore = ScheduledChore.objects.get(pk=kwargs['sc_id'])
    if request.user != scheduledChore.person:
        return HttpResponseNotFound()
    people = Person.objects.all().order_by('-weekly_modifier')
    oldPerson = scheduledChore.person
    # make sure we don't give it back to the same person...
    if people[0] == oldPerson:
        newPerson = people[1]
    else:
        newPerson = people[0]
    oldPerson.weekly_modifier += 1
    oldPerson.save()
    scheduledChore.person = newPerson
    scheduledChore.save()
    return HttpResponseRedirect('/')

def give_away_daily(request, **kwargs):
    if request.method != 'POST':
        return HttpResponseNotFound()
    scheduledChore = ScheduledChore.objects.get(pk=kwargs['sc_id'])
    if request.user != scheduledChore.person:
        return HttpResponseNotFound()
    people = Person.objects.all().order_by('-daily_modifier')
    oldPerson = scheduledChore.person
    # make sure we don't give it back to the same person...
    if people[0] == oldPerson:
        newPerson = people[1]
    else:
        newPerson = people[0]
    oldPerson.weekly_modifier += 1
    oldPerson.save()
    scheduledChore.person = newPerson
    scheduledChore.save()
    return HttpResponseRedirect('/')
