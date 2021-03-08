# Generated by Django 3.1.5 on 2021-03-08 00:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MaterialsProjectStructure',
            fields=[
                ('structure_json', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('nsites', models.IntegerField()),
                ('nelement', models.IntegerField()),
                ('chemical_system', models.CharField(max_length=25)),
                ('density', models.FloatField()),
                ('spacegroup', models.IntegerField()),
                ('formula_full', models.CharField(max_length=25)),
                ('formula_reduced', models.CharField(max_length=25)),
                ('formula_anonymous', models.CharField(max_length=25)),
                ('id', models.CharField(max_length=12, primary_key=True, serialize=False)),
                ('final_energy', models.FloatField(blank=True, null=True)),
                ('final_energy_per_atom', models.FloatField(blank=True, null=True)),
                ('formation_energy_per_atom', models.FloatField(blank=True, null=True)),
                ('e_above_hull', models.FloatField(blank=True, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Pathway',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('element', models.CharField(max_length=2)),
                ('isite', models.CharField(max_length=100)),
                ('msite', models.CharField(max_length=100)),
                ('esite', models.CharField(max_length=100)),
                ('iindex', models.IntegerField()),
                ('eindex', models.IntegerField()),
                ('length', models.FloatField()),
                ('atomic_fraction', models.FloatField()),
                ('nsites_777', models.IntegerField()),
                ('nsites_101010', models.IntegerField()),
                ('nsites_121212', models.IntegerField()),
                ('structure', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pathways', to='diffusion.materialsprojectstructure')),
            ],
        ),
        migrations.CreateModel(
            name='EmpiricalMeasures',
            fields=[
                ('status', models.CharField(choices=[('S', 'Scheduled'), ('C', 'Completed'), ('F', 'Failed')], default='S', max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('oxidation_state', models.IntegerField(blank=True, null=True)),
                ('dimensionality', models.IntegerField(blank=True, null=True)),
                ('dimensionality_cumlengths', models.IntegerField(blank=True, null=True)),
                ('ewald_energy', models.FloatField(blank=True, null=True)),
                ('ionic_radii_overlap_cations', models.FloatField(blank=True, null=True)),
                ('ionic_radii_overlap_anions', models.FloatField(blank=True, null=True)),
                ('pathway', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='diffusion.pathway')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VaspCalcA',
            fields=[
                ('status', models.CharField(choices=[('S', 'Scheduled'), ('C', 'Completed'), ('F', 'Failed')], default='S', max_length=1)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('energy_start', models.FloatField(blank=True, null=True)),
                ('energy_midpoint', models.FloatField(blank=True, null=True)),
                ('energy_end', models.FloatField(blank=True, null=True)),
                ('energy_barrier', models.FloatField(blank=True, null=True)),
                ('pathway', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='diffusion.pathway')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
