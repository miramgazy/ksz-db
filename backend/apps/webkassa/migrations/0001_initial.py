from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('companies', '0013_company_bin'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebkassaCTO',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150, unique=True, verbose_name='Название ЦТО')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
            ],
            options={
                'verbose_name': 'Обслуживающее ЦТО',
                'verbose_name_plural': 'Обслуживающие ЦТО',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='WebkassaCashRegister',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cto', models.CharField(blank=True, db_index=True, max_length=150, verbose_name='Обслуживающее ЦТО')),
                ('name', models.CharField(max_length=255, verbose_name='Название кассы')),
                ('serial_number', models.CharField(db_index=True, max_length=100, unique=True, verbose_name='Заводской номер')),
                ('status', models.CharField(blank=True, max_length=100, verbose_name='Статус')),
                ('ofd', models.CharField(blank=True, max_length=255, verbose_name='ОФД')),
                ('bin_iin', models.CharField(blank=True, db_index=True, max_length=30, verbose_name='БИН / ИИН')),
                ('organization', models.CharField(blank=True, db_index=True, max_length=255, verbose_name='Организация (из WebKassa)')),
                ('expires_at', models.DateField(blank=True, db_index=True, null=True, verbose_name='Срок окончания')),
                ('auto_matched', models.BooleanField(default=False, verbose_name='Привязано автоматически по БИН/ИИН')),
                ('comment', models.TextField(blank=True, verbose_name='Примечание инженера')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Дата обновления')),
                ('company', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cash_registers', to='companies.company', verbose_name='Привязанное заведение')),
            ],
            options={
                'verbose_name': 'Касса WebKassa',
                'verbose_name_plural': 'Кассы WebKassa',
                'ordering': ['expires_at', 'name'],
            },
        ),
    ]
