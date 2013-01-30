from django.db import models

class Gnubuildid(models.Model):
    """
    Table to store GNU_BUILD_ID details
    """
    elfname = models.TextField()
    instpath = models.TextField()
    build_id = models.TextField()
    rpm_name = models.TextField()
    distro = models.TextField()
    kojibuildid = models.IntegerField()

class Darkuser(models.Model):
    """
    Table to store darkserver write users
    """
    name = models.TextField()
    password = models.TextField()
    comments = models.TextField()
