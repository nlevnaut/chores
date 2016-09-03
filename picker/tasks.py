from celery import Celery
from celery import shared_task, chain, group, chord, Task
from django.utils import timezone
from celery.decorators import periodic_task
from celery.task.schedules import crontab
from picker.models import *
from collections import deque
import random

@periodic_task(name='pick_weekly', run_every=crontab(hour=9, minute=0, day_of_week="sun"))
def pick_weekly():
    check_weekly_done()
    # randomize chores
    chores = list(Chore.objects.filter(frequency='weekly'))
    random.shuffle(chores)
    # make sure people with the highest weekly modifier get chores first.
    people = list(Person.objects.all())
    for p in people:
        p.weekly_modifier += 1
        p.save()

    sorted_people = sorted(people, key=lambda x: x.weekly_modifier, reverse=True)
    if (chores is None):
        print('No chores!')
        return
    elif (people is None):
        print('No people!')
        return

    for c in chores:
        p = sorted_people[0]
        s = ScheduledChore()
        s.person = p
        s.chore = c
        s.date = timezone.now()
        s.day = 0
        s.save()
        p.weekly_modifier -= 1
        p.save()
        sorted_people = sorted(people, key=lambda x: x.weekly_modifier, reverse=True)

@periodic_task(name='pick_daily', run_every=crontab(hour=9, minute=0, day_of_week="sun"))
def pick_daily():
    check_daily_done()
    people = list(Person.objects.all())
    if len(people) == 0:
        print("No people!!!!!")
        return

    chores = list(Chore.objects.filter(frequency='daily'))

    # increase everyone's modifier at the beginning of the week
    # assume everyone does one chore once. the people who do extra benefit here.
    for p in people:
        p.daily_modifier += len(chores)
        p.last_picked = -1
        p.save()

    sorted_people = sorted(people, key=lambda p: p.last_picked)
    sorted_people = sorted(sorted_people, key=lambda p: p.daily_modifier, reverse=True)

    for i in range(0, 7):
        j = 0
        for c in chores:
            p = sorted_people[j % len(sorted_people)]

            s = ScheduledChore()
            s.date = timezone.now()
            s.person = p
            s.day = i
            s.chore = c
            p.daily_modifier -= 1
            p.last_picked = i
            p.save()
            s.save()
            j += 1
        sorted_people = sorted(sorted_people, key=lambda p: p.last_picked)
        print(sorted_people)
        sorted_people = sorted(sorted_people, key=lambda p: p.daily_modifier, reverse=True)
        print(sorted_people)
        for p in sorted_people:
            print(p.name + ': ' + str(p.daily_modifier))

def reset_all_modifiers():
	for p in Person.objects.all():
		p.daily_modifier = 0
		p.weekly_modifier = 0
		p.save()

def check_daily_done():
    chores = ScheduledChore.objects.filter(done=False, chore__frequency='daily')
    for chore in chores:
        #chore.person.daily_modifier += 1
        #chore.person.save()
        chore.done = True
        chore.save()

def check_weekly_done():
    chores = ScheduledChore.objects.filter(done=False, chore__frequency='weekly')
    for chore in chores:
        #chore.person.weekly_modifier += 1
        #chore.person.save()
        chore.done = True
        chore.save()

def transfer_chore(scheduledChore, newPerson):
    if scheduledChore.frequency == 'weekly':
        scheduledChore.person.weekly_modifier += 1
        newPerson.weekly_modifier += 1
    elif scheduledChore.frequency == 'daily':
        scheduledChore.person.daily_modifier += 1
        newPerson.daily_modifier += 1
        
    scheduledChore.person.save()
    newPerson.save()
    scheduledChore.person = newPerson
    scheduledChore.save()
