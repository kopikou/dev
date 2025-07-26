from django.db import models

# Create your models here.
from django.db import models

class FDBSection(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        
    def __str__(self):
        return self.name