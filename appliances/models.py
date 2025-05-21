from django.db import models
from django.contrib.auth.models import User

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Appliance(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='appliances')
    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.name} ({self.category.name})"

class BorrowRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    appliance = models.ForeignKey(Appliance, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    approved = models.BooleanField(default=False)  # admin can approve later
    declined = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)
    
    # New fields for borrower information
    full_name = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    planned_borrow_date = models.DateField(null=True, blank=True)
    planned_return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} requests {self.quantity} {self.appliance.name}(s)"
