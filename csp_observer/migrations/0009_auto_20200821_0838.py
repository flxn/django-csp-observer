# Generated by Django 3.0.5 on 2020-08-21 08:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csp_observer', '0008_auto_20200819_1955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storedconfig',
            name='key',
            field=models.TextField(unique=True),
        ),
    ]