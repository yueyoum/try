# -*- coding: utf-8 -*-
import os

from django.db import models
from django.db.models.signals import post_delete


from .app_settings import (
    UPLOAD_AVATAR_UPLOAD_ROOT,
)


class UploadedImage(models.Model):
    uid = models.IntegerField(unique=True)
    image = models.CharField(max_length=128)

    def get_image_path(self):
        path = os.path.join(UPLOAD_AVATAR_UPLOAD_ROOT, self.image)
        if not os.path.exists(path):
            return None
        return path

    def delete_image(self):
        path = self.get_image_path()
        if path:
            try:
                os.unlink(path)
            except OSError:
                pass


def _delete_avatar_on_disk(sender, instance, *args, **kwargs):
    instance.delete_image()


post_delete.connect(_delete_avatar_on_disk, sender=UploadedImage)

