from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse

from dcim.models import BaseInterface, Device
from extras.models import ConfigContextModel
from extras.querysets import ConfigContextModelQuerySet
from extras.utils import extras_features
from netbox.models import OrganizationalModel, PrimaryModel
from utilities.fields import NaturalOrderingField
from utilities.ordering import naturalize_interface
from utilities.query_functions import CollateAsChar
from utilities.querysets import RestrictedQuerySet
from .choices import *


__all__ = (
    'Cluster',
    'ClusterGroup',
    'ClusterType',
    'VirtualMachine',
    'VMInterface',
)


#
# Cluster types
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class ClusterType(OrganizationalModel):
    """
    A type of Cluster.
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

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['name', 'slug', 'description']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:clustertype', args=[self.pk])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.description,
        )


#
# Cluster groups
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'webhooks')
class ClusterGroup(OrganizationalModel):
    """
    An organizational group of Clusters.
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

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['name', 'slug', 'description']

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:clustergroup', args=[self.pk])

    def to_csv(self):
        return (
            self.name,
            self.slug,
            self.description,
        )


#
# Clusters
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class Cluster(PrimaryModel):
    """
    A cluster of VirtualMachines. Each Cluster may optionally be associated with one or more Devices.
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    type = models.ForeignKey(
        to=ClusterType,
        on_delete=models.PROTECT,
        related_name='clusters'
    )
    group = models.ForeignKey(
        to=ClusterGroup,
        on_delete=models.PROTECT,
        related_name='clusters',
        blank=True,
        null=True
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='clusters',
        blank=True,
        null=True
    )
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.PROTECT,
        related_name='clusters',
        blank=True,
        null=True
    )
    comments = models.TextField(
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = ['name', 'type', 'group', 'site', 'comments']
    clone_fields = [
        'type', 'group', 'tenant', 'site',
    ]

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:cluster', args=[self.pk])

    def clean(self):
        super().clean()

        # If the Cluster is assigned to a Site, verify that all host Devices belong to that Site.
        if self.pk and self.site:
            nonsite_devices = Device.objects.filter(cluster=self).exclude(site=self.site).count()
            if nonsite_devices:
                raise ValidationError({
                    'site': "{} devices are assigned as hosts for this cluster but are not in site {}".format(
                        nonsite_devices, self.site
                    )
                })

    def to_csv(self):
        return (
            self.name,
            self.type.name,
            self.group.name if self.group else None,
            self.site.name if self.site else None,
            self.tenant.name if self.tenant else None,
            self.comments,
        )


#
# Virtual machines
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class VirtualMachine(PrimaryModel, ConfigContextModel):
    """
    A virtual machine which runs inside a Cluster.
    """
    cluster = models.ForeignKey(
        to='virtualization.Cluster',
        on_delete=models.PROTECT,
        related_name='virtual_machines'
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='virtual_machines',
        blank=True,
        null=True
    )
    platform = models.ForeignKey(
        to='dcim.Platform',
        on_delete=models.SET_NULL,
        related_name='virtual_machines',
        blank=True,
        null=True
    )
    name = models.CharField(
        max_length=64
    )
    _name = NaturalOrderingField(
        target_field='name',
        max_length=100,
        blank=True
    )
    status = models.CharField(
        max_length=50,
        choices=VirtualMachineStatusChoices,
        default=VirtualMachineStatusChoices.STATUS_ACTIVE,
        verbose_name='Status'
    )
    role = models.ForeignKey(
        to='dcim.DeviceRole',
        on_delete=models.PROTECT,
        related_name='virtual_machines',
        limit_choices_to={'vm_role': True},
        blank=True,
        null=True
    )
    primary_ip4 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Primary IPv4'
    )
    primary_ip6 = models.OneToOneField(
        to='ipam.IPAddress',
        on_delete=models.SET_NULL,
        related_name='+',
        blank=True,
        null=True,
        verbose_name='Primary IPv6'
    )
    vcpus = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='vCPUs',
        validators=(
            MinValueValidator(0.01),
        )
    )
    memory = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Memory (MB)'
    )
    disk = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name='Disk (GB)'
    )
    comments = models.TextField(
        blank=True
    )
    secrets = GenericRelation(
        to='secrets.Secret',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='virtual_machine'
    )

    objects = ConfigContextModelQuerySet.as_manager()

    csv_headers = [
        'name', 'status', 'role', 'cluster', 'tenant', 'platform', 'vcpus', 'memory', 'disk', 'comments',
    ]
    clone_fields = [
        'cluster', 'tenant', 'platform', 'status', 'role', 'vcpus', 'memory', 'disk',
    ]

    class Meta:
        ordering = ('_name', 'pk')  # Name may be non-unique
        unique_together = [
            ['cluster', 'tenant', 'name']
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:virtualmachine', args=[self.pk])

    def validate_unique(self, exclude=None):

        # Check for a duplicate name on a VM assigned to the same Cluster and no Tenant. This is necessary
        # because Django does not consider two NULL fields to be equal, and thus will not trigger a violation
        # of the uniqueness constraint without manual intervention.
        if self.tenant is None and VirtualMachine.objects.exclude(pk=self.pk).filter(
                name=self.name, cluster=self.cluster, tenant__isnull=True
        ):
            raise ValidationError({
                'name': 'A virtual machine with this name already exists in the assigned cluster.'
            })

        super().validate_unique(exclude)

    def clean(self):
        super().clean()

        # Validate primary IP addresses
        interfaces = self.interfaces.all()
        for field in ['primary_ip4', 'primary_ip6']:
            ip = getattr(self, field)
            if ip is not None:
                if ip.assigned_object in interfaces:
                    pass
                elif ip.nat_inside is not None and ip.nat_inside.assigned_object in interfaces:
                    pass
                else:
                    raise ValidationError({
                        field: f"The specified IP address ({ip}) is not assigned to this VM.",
                    })

    def to_csv(self):
        return (
            self.name,
            self.get_status_display(),
            self.role.name if self.role else None,
            self.cluster.name,
            self.tenant.name if self.tenant else None,
            self.platform.name if self.platform else None,
            self.vcpus,
            self.memory,
            self.disk,
            self.comments,
        )

    def get_status_class(self):
        return VirtualMachineStatusChoices.CSS_CLASSES.get(self.status)

    @property
    def primary_ip(self):
        if settings.PREFER_IPV4 and self.primary_ip4:
            return self.primary_ip4
        elif self.primary_ip6:
            return self.primary_ip6
        elif self.primary_ip4:
            return self.primary_ip4
        else:
            return None

    @property
    def site(self):
        return self.cluster.site


#
# Interfaces
#

@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class VMInterface(PrimaryModel, BaseInterface):
    virtual_machine = models.ForeignKey(
        to='virtualization.VirtualMachine',
        on_delete=models.CASCADE,
        related_name='interfaces'
    )
    name = models.CharField(
        max_length=64
    )
    _name = NaturalOrderingField(
        target_field='name',
        naturalize_function=naturalize_interface,
        max_length=100,
        blank=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )
    parent = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        related_name='child_interfaces',
        null=True,
        blank=True,
        verbose_name='Parent interface'
    )
    untagged_vlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.SET_NULL,
        related_name='vminterfaces_as_untagged',
        null=True,
        blank=True,
        verbose_name='Untagged VLAN'
    )
    tagged_vlans = models.ManyToManyField(
        to='ipam.VLAN',
        related_name='vminterfaces_as_tagged',
        blank=True,
        verbose_name='Tagged VLANs'
    )
    ip_addresses = GenericRelation(
        to='ipam.IPAddress',
        content_type_field='assigned_object_type',
        object_id_field='assigned_object_id',
        related_query_name='vminterface'
    )

    objects = RestrictedQuerySet.as_manager()

    csv_headers = [
        'virtual_machine', 'name', 'enabled', 'mac_address', 'mtu', 'description', 'mode',
    ]

    class Meta:
        verbose_name = 'interface'
        ordering = ('virtual_machine', CollateAsChar('_name'))
        unique_together = ('virtual_machine', 'name')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('virtualization:vminterface', kwargs={'pk': self.pk})

    def to_csv(self):
        return (
            self.virtual_machine.name,
            self.name,
            self.enabled,
            self.parent.name if self.parent else None,
            self.mac_address,
            self.mtu,
            self.description,
            self.get_mode_display(),
        )

    def clean(self):
        super().clean()

        # An interface's parent must belong to the same virtual machine
        if self.parent and self.parent.virtual_machine != self.virtual_machine:
            raise ValidationError({
                'parent': f"The selected parent interface ({self.parent}) belongs to a different virtual machine "
                          f"({self.parent.virtual_machine})."
            })

        # An interface cannot be its own parent
        if self.pk and self.parent_id == self.pk:
            raise ValidationError({'parent': "An interface cannot be its own parent."})

        # Validate untagged VLAN
        if self.untagged_vlan and self.untagged_vlan.site not in [self.virtual_machine.site, None]:
            raise ValidationError({
                'untagged_vlan': f"The untagged VLAN ({self.untagged_vlan}) must belong to the same site as the "
                                 f"interface's parent virtual machine, or it must be global"
            })

    def to_objectchange(self, action):
        # Annotate the parent VirtualMachine
        return super().to_objectchange(action, related_object=self.virtual_machine)

    @property
    def parent_object(self):
        return self.virtual_machine
