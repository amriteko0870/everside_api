# Generated by Django 4.0.3 on 2022-04-28 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apiApp', '0002_everside_nps_clinics'),
    ]

    operations = [
        migrations.CreateModel(
            name='everside_nps_word_frequency',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('word', models.CharField(max_length=100)),
                ('question_type', models.CharField(max_length=100)),
                ('frequency', models.CharField(max_length=100)),
            ],
        ),
    ]
