from django.db import migrations, models


def mark_existing_good_receipts_as_counted(apps, schema_editor):
    Receiving = apps.get_model("accounts", "Receiving")
    Receiving.objects.filter(condition="GOOD").update(inventory_updated=True)


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0005_receiving_condition"),
    ]

    operations = [
        migrations.AddField(
            model_name="receiving",
            name="inventory_updated",
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(
            mark_existing_good_receipts_as_counted,
            migrations.RunPython.noop,
        ),
    ]
