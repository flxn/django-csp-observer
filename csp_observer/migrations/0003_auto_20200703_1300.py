# Generated by Django 3.0.5 on 2020-07-03 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csp_observer', '0002_auto_20200618_1232'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cspreport',
            name='disposition',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='cspreport',
            name='original_policy',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
