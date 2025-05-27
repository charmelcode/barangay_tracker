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
    image = models.ImageField(upload_to='appliance_images/', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.category.name})"

class BorrowRequest(models.Model):
    UNRETURNED_STATUS_CHOICES = [
        ('pending', 'Pending Return'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
        ('replaced', 'Replaced'),
        ('paid', 'Paid'),
    ]

    ITEM_CONDITION_CHOICES = [
        ('good', 'Good Condition'),
        ('damaged', 'Damaged'),
        ('lost', 'Lost'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    appliance = models.ForeignKey(Appliance, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    approved = models.BooleanField(default=False)
    declined = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)
    
    # Fields for tracking returns
    returned_quantity = models.PositiveIntegerField(default=0)
    unreturned_quantity = models.PositiveIntegerField(default=0)
    unreturned_status = models.CharField(
        max_length=20, 
        choices=UNRETURNED_STATUS_CHOICES,
        null=True, 
        blank=True
    )
    unreturned_reason = models.TextField(null=True, blank=True)
    
    # Fields for tracking item conditions
    item_conditions = models.JSONField(default=dict, blank=True)
    resolution_status = models.JSONField(default=dict, blank=True)
    
    # Borrower information
    full_name = models.CharField(max_length=255, null=True, blank=True)
    contact_number = models.CharField(max_length=20, null=True, blank=True)
    location = models.TextField(null=True, blank=True)
    planned_borrow_date = models.DateField(null=True, blank=True)
    planned_return_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} requests {self.quantity} {self.appliance.name}(s)"

    def save(self, *args, **kwargs):
        # If this is a new request, set unreturned_quantity to the total quantity
        if not self.pk:
            self.unreturned_quantity = self.quantity
        super().save(*args, **kwargs)
