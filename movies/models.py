from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    title = models.CharField(max_length=255)
    year = models.CharField(max_length=10)
    genre = models.CharField(max_length=255)
    language = models.CharField(max_length=100)
    cast = models.TextField()
    imdb = models.FloatField(null=True, blank=True)
    rt = models.FloatField(null=True, blank=True)
    google = models.FloatField(null=True, blank=True)
    poster = models.URLField()
    added_by = models.CharField(max_length=255)

    def __str__(self):
        return self.title

class WatchStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'movie')  # one status per user/movie

    def __str__(self):
        return f"{self.user.username} - {self.movie.title} - {'Watched' if self.watched else 'Not Watched'}"
