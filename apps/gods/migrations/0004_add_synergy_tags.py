# Generated manually

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gods', '0003_alter_god_pantheon'),
    ]

    operations = [
        migrations.CreateModel(
            name='GodSynergyTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tag', models.CharField(db_index=True, max_length=50)),
                ('god', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='synergy_tags', to='gods.god')),
            ],
            options={
                'unique_together': {('god', 'tag')},
            },
        ),
    ]
