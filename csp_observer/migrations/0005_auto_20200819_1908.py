# Generated by Django 3.0.5 on 2020-08-19 19:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('csp_observer', '0004_csprule_is_custom_rule'),
    ]

    operations = [
        migrations.CreateModel(
            name='GlobalCspRule',
            fields=[
                ('csprule_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='csp_observer.CspRule')),
                ('global_id', models.CharField(max_length=255)),
            ],
            bases=('csp_observer.csprule',),
        ),
        migrations.RemoveField(
            model_name='csprule',
            name='is_custom_rule',
        ),
        migrations.AddField(
            model_name='csprule',
            name='cause',
            field=models.CharField(choices=[('EXTENSION', 'Browser Extension'), ('BROWSER', 'Web Browser'), ('MALWARE', 'Malware'), ('OTHER', 'Other')], default='OTHER', max_length=255),
        ),
    ]