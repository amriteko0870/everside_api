# Generated by Django 4.0.3 on 2022-04-28 09:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apiApp', '0003_everside_nps_word_frequency'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='everside_nps_clinics',
            name='nps',
        ),
    ]
