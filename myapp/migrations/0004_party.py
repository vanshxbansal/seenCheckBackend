# Generated by Django 5.1.3 on 2024-11-16 10:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_userprofile'),
    ]

    operations = [
        migrations.CreateModel(
            name='Party',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('party_name', models.CharField(max_length=255)),
                ('party_description', models.TextField()),
                ('party_location', models.CharField(max_length=255)),
                ('party_date', models.DateTimeField()),
                ('party_time', models.TimeField()),
            ],
        ),
    ]
