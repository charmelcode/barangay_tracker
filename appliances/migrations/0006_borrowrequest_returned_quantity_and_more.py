# Generated by Django 5.2.1 on 2025-05-22 01:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appliances', '0005_borrowrequest_contact_number_borrowrequest_full_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrowrequest',
            name='returned_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='borrowrequest',
            name='unreturned_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='borrowrequest',
            name='unreturned_reason',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='borrowrequest',
            name='unreturned_status',
            field=models.CharField(blank=True, choices=[('pending', 'Pending Return'), ('lost', 'Lost'), ('damaged', 'Damaged')], max_length=20, null=True),
        ),
    ]
