from django.db.models import signals
from django.dispatch import receiver
from django.db.models import FileField

# should it need to limit signal senders to reduce possible performance issues?


@receiver(signals.post_delete)
def delete_image_file(sender, **kwargs):
    """
    Delete all files from for the deleted object
    """
    inst = kwargs.get("instance")
    if inst is None:
        return

    for field in sender._meta.get_fields():

        if not isinstance(field, FileField):
            continue

        # get field value
        value = getattr(inst, field.name, None)

        if value is None:
            continue

        value.delete(save=False)

