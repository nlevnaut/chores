from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import UserManager

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email = self.normalize_email(email), **extra_fields)
        user.is_active = True 
        user.set_password(password)
        user.save(using = self._db)
        return user

    def create_user(self, email, password, **extra_fields):
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        user = self.create_user(email=email, password=password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class Person(AbstractBaseUser):
    def __str__(self):
        return self.name
    def __unicode__(self):
        return self.name

    def has_perm(self, perm, obj=None):
        if self.is_superuser:
            return True
        else:
            return False

    def has_module_perms(self, app_label):
        if self.is_superuser:
            return True
        return _user_has_module_perms(self, app_label)

    def get_full_name(self):
        return self.name

    def get_short_name(self): return self.name.split(' ')[0]


    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=320, unique=True)
    objects = CustomUserManager()
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    daily_modifier = models.IntegerField(default=0)
    weekly_modifier = models.IntegerField(default=0)
    last_picked = models.PositiveIntegerField(default=0)

    USERNAME_FIELD = 'email'

class Chore(models.Model):
    def __str__(self):
        return self.name
    def __unicode__(self):
        return self.name

    name = models.CharField(max_length=30)
    description = models.CharField(max_length=240)
    frequency = models.CharField(max_length=30)

class ScheduledChore(models.Model):
    def __str__(self):
        return self.chore.name + ': ' + self.person.name
    def __unicode__(self):
        return self.chore.name + ': ' + self.person.name

    day = models.PositiveIntegerField()
    date = models.DateTimeField()
    chore = models.ForeignKey('Chore')
    person = models.ForeignKey('Person')
    done = models.BooleanField(default=False)
