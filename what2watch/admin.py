from django.contrib import admin

# Register your models here.

from .models import Movie, WatchStatus

admin.site.register(Movie)
admin.site.register(WatchStatus)
