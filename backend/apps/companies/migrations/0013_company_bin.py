from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0012_company_license_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='company',
            name='bin',
            field=models.CharField(blank=True, db_index=True, max_length=20, verbose_name='БИН / ИИН'),
        ),
    ]
