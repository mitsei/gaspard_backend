from django.db import models

# Create your models here.
class Post(models.Model):
    value=models.CharField(max_length=20)
    key=models.CharField(max_length=20, unique=True)

    def __unicode__(self):
        return self.key


class Headers(models.Model):
    key = models.CharField(max_length=20)
    value = models.CharField(max_length=100)

    def __unicode__(self):
        return self.key

class Bank(models.Model):
    key=models.CharField(max_length=20)
    value= models.CharField(max_length=100)

class Questions(models.Model):
   # key = models.CharField(max_length=20)
    value = models.CharField(max_length=10000)

    def __unicode__(self):
        return self.value