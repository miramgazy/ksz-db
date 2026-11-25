from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webkassa', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='webkassacashregister',
            name='is_active',
            field=models.BooleanField(db_index=True, default=True, verbose_name='Активна'),
        ),
    ]
