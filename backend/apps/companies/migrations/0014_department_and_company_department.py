from django.db import migrations, models

def init_departments(apps, schema_editor):
    Department = apps.get_model('companies', 'Department')
    Company = apps.get_model('companies', 'Company')

    initial_departments = ['Запад', 'Алматы', 'Шымкент', 'Астана', 'Караганды']
    for dept_name in initial_departments:
        Department.objects.get_or_create(name=dept_name)

    Company.objects.all().update(department='Запад')

def reverse_departments(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0013_company_bin'),
    ]

    operations = [
        migrations.CreateModel(
            name='Department',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Департамент')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')),
            ],
            options={
                'verbose_name': 'Департамент',
                'verbose_name_plural': 'Департаменты',
                'ordering': ['name'],
            },
        ),
        migrations.AddField(
            model_name='company',
            name='department',
            field=models.CharField(blank=True, db_index=True, default='Запад', max_length=100, verbose_name='Департамент'),
        ),
        migrations.RunPython(init_departments, reverse_departments),
    ]
