# Generated by Django 4.0.1 on 2024-04-07 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('model', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='code',
            field=models.CharField(default='B0', max_length=50),
            preserve_default=False,
        ),
    ]
