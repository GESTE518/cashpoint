# Generated by Django 5.1.2 on 2024-10-31 18:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('transactions', '0008_alter_expense_options_resume'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='expense',
            options={},
        ),
        migrations.DeleteModel(
            name='Resume',
        ),
    ]
