# Generated by Django 3.2.6 on 2022-01-22 16:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_post_property_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='boundaries',
            name='postcode',
            field=models.CharField(db_index=True, max_length=10, null=True),
        ),
    ]
