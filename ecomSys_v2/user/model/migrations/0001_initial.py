# Generated by Django 4.1.13 on 2024-03-30 16:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=50)),
                ('email', models.CharField(max_length=50)),
                ('mobile', models.CharField(max_length=10)),
                ('password', models.CharField(max_length=200)),
                ('address', models.CharField(default=None, max_length=200)),
                ('role', models.PositiveIntegerField(default=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('deleted', models.BooleanField(default=False)),
            ],
        ),
    ]
