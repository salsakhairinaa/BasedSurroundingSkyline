# Generated by Django 2.1.5 on 2020-05-24 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spatialskyline', '0002_query'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spatialskyline',
            name='tipe_poi',
            field=models.CharField(choices=[('restaurant', 'Restaurant'), ('lodging', 'Lodging'), ('cafe', 'Cafe'), ('supermarket', 'Supermarket'), ('parking', 'Parking'), ('shopping_mall', 'Shopping Mall')], max_length=1),
        ),
    ]
