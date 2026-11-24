from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0011_cleanup_inactive_companies_its'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='license_data',
            field=models.JSONField(blank=True, default=dict, verbose_name='Информация о лицензиях'),
        ),
        migrations.AddField(
            model_name='company',
            name='license_updated_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Дата обновления лицензии'),
        ),
        migrations.AddField(
            model_name='company',
            name='last_license_error',
            field=models.TextField(blank=True, verbose_name='Последняя ошибка обновления лицензии'),
        ),
    ]
