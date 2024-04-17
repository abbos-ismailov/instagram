# Generated by Django 5.0.3 on 2024-04-03 11:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_user_photo_userconfirmation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='auth_status',
            field=models.CharField(choices=[('new', 'new'), ('code_verified', 'code_verified'), ('done', 'done'), ('photo_done', 'photo_done')], default='new', max_length=40),
        ),
    ]
