# Generated by Django 3.1 on 2020-08-27 07:06

from django.db import migrations, models
import static_content.utils


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='option',
            name='media',
            field=models.FileField(max_length=255, upload_to=static_content.utils.upload_to),
        ),
    ]
