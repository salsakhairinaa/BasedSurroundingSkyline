# Generated by Django 2.1.5 on 2020-05-09 08:03

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='spatialSkyline',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('daerah', models.CharField(max_length=100)),
                ('tipe_poi', models.CharField(max_length=100)),
            ],
        ),
    ]
