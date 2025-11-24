from django.db import models
from accounts.models import User

class ServingBuilding(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'serving_buildings'
    
    def __str__(self):
        return self.name

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    serving_building = models.ForeignKey(ServingBuilding, on_delete=models.CASCADE)
    flat_number = models.CharField(max_length=50)
    landmark = models.CharField(max_length=200, blank=True)
    is_default = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'addresses'
