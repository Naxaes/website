import uuid

from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.


class DatedModel(models.Model):
    """"
    Models inherit create_at and modified_at to see whenever a model is saved or modified
    """
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)
    modified_at = models.DateTimeField(_('modified_at'), auto_now=True)
    uid = models.UUIDField(default=uuid.uuid4, help_text=_('Unique ID for this model'))

    class Meta:
        abstract = True
