# Generated by Django 2.1.2 on 2019-04-28 01:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('glbs', '0012_tb_fact_adminip_info_tb_fact_detecttask_info'),
    ]

    operations = [
        migrations.CreateModel(
            name='tb_fact_detectdeviceavailability_info',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('admin_ip', models.CharField(max_length=256)),
                ('vip_address', models.CharField(max_length=256)),
                ('availability', models.CharField(max_length=256)),
            ],
        ),
    ]
