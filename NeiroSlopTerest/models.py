from django.db import models

class Pin(models.Model):
    title = models.CharField()
    description = models.CharField(default="", blank=True)
    image_url = models.CharField()