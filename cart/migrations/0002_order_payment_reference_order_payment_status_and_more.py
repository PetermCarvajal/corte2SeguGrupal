# Generated by Django 5.1.7 on 2025-03-31 04:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='payment_reference',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='order',
            name='payment_status',
            field=models.CharField(choices=[('pendiente', 'Pendiente'), ('completado', 'Completado'), ('fallido', 'Fallido'), ('reembolsado', 'Reembolsado')], default='pendiente', max_length=20),
        ),
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('paypal', 'PayPal'), ('nequi', 'Nequi'), ('credit_card', 'Tarjeta de Crédito'), ('debit_card', 'Tarjeta de Débito')], default='paypal', max_length=20),
        ),
    ]
