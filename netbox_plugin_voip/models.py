from django.db import models
from django.core.validators import RegexValidator
from django.db.models.deletion import SET_NULL
from django.urls import reverse

from netbox.models import NestedGroupModel, PrimaryModel 
from extras.utils import extras_features
from dcim.fields import ASNField
from netbox.models import ChangeLoggedModel
from ipam.fields import IPAddressField
from utilities.querysets import RestrictedQuerySet

number_validator = RegexValidator(
    r"^\+?[0-9A-D\#\*]*$",
    "DIDs can only contain: leading +, digits 0-9; chars A, B, C, D; # and *"
)

class DIDNumbers(ChangeLoggedModel):
    """A DID represents a single telephone number of an arbitrary format.
    A DID can contain only valid DTMF characters and leading plus sign for E.164 support:
      - leading plus ("+") sign (optional)
      - digits 0-9
      - characters A, B, C, D
      - pound sign ("#")
      - asterisk sign ("*")
    DID values can be not unique.
    Partition is a mandatory option representing a number partition. DID and Partition are globally unique.
    A DID can optionally be assigned with Provider and Region relations.
    A DID can contain an optional Description.
    A DID can optionally be tagged with Tags.
    """
    #site = models.ForeignKey(to="dcim.Site", on_delete=models.SET_NULL, blank=True, null=True)
    did = models.CharField(max_length=32,validators=[number_validator])
    description = models.CharField(max_length=200, blank=True)
    provider = models.ForeignKey(to="circuits.Provider",on_delete=models.SET_NULL,blank=True,null=True,related_name="provider_set")
    partition = models.ForeignKey(to="netbox_plugin_voip.Partition",on_delete=models.SET_NULL,blank=True,null=True)
    route_option = models.BooleanField(blank=True,null=True)
    called_party_mask = models.IntegerField(blank=True,null=True)

    class Meta:
        unique_together = ("did","partition",)


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class Partition(PrimaryModel):
    """
    A Partition represents an Route Partition served by the NetBox owner.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    comments = models.TextField(
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['name', 'slug', 'description', 'comments']
    clone_fields = ['description']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('tenancy:tenant', args=[self.pk])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.description,
            self.comments,
        )

