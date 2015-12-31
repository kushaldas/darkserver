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
    kojitype = models.TextField()
    rpm_url = models.TextField()