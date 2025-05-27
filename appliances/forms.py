from django import forms
from .models import BorrowRequest, Appliance
from django.utils import timezone

class BorrowRequestForm(forms.ModelForm):
    planned_borrow_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().isoformat()}),
        help_text="Select the date you want to borrow the appliance"
    )
    planned_return_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': timezone.now().date().isoformat()}),
        help_text="Select the date you will return the appliance"
    )

    class Meta:
        model = BorrowRequest
        fields = [
            'quantity', 
            'full_name', 
            'contact_number', 
            'location',
            'planned_borrow_date',
            'planned_return_date'
        ]
        widgets = {
            'location': forms.Textarea(attrs={'rows': 3}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'e.g., +63 912 345 6789'}),
        }

    def __init__(self, *args, **kwargs):
        self.appliance = kwargs.pop('appliance', None)
        super().__init__(*args, **kwargs)
        
        # Add placeholders and classes
        self.fields['full_name'].widget.attrs.update({
            'placeholder': 'Enter your full name',
            'class': 'form-input'
        })
        self.fields['location'].widget.attrs.update({
            'placeholder': 'Enter complete address where the appliance will be used',
            'class': 'form-input'
        })
        
        # Make all fields required
        for field in self.fields:
            self.fields[field].required = True

    def clean(self):
        cleaned_data = super().clean()
        planned_borrow_date = cleaned_data.get('planned_borrow_date')
        planned_return_date = cleaned_data.get('planned_return_date')
        quantity = cleaned_data.get('quantity')

        if planned_borrow_date and planned_return_date:
            if planned_borrow_date < timezone.now().date():
                raise forms.ValidationError("Planned borrow date cannot be in the past.")
            
            if planned_return_date < planned_borrow_date:
                raise forms.ValidationError("Return date must be after the borrow date.")

        if self.appliance and quantity:
            if quantity > self.appliance.quantity:
                raise forms.ValidationError(
                    f"Only {self.appliance.quantity} {self.appliance.name}(s) available."
                )
            if quantity <= 0:
                raise forms.ValidationError("Quantity must be at least 1.")

        return cleaned_data

class ApplianceForm(forms.ModelForm):
    class Meta:
        model = Appliance
        fields = ['name', 'description', 'category', 'quantity', 'image'] 