from circuits.models import Circuit
from dcim.models import Site, Rack, Device, RackReservation
from ipam.models import Aggregate, IPAddress, Prefix, VLAN, VRF
from netbox.views import generic
from utilities.tables import paginate_table
from virtualization.models import VirtualMachine, Cluster
from . import filtersets, forms, tables
from .models import Tenant, TenantGroup


#
# Tenant groups
#

class TenantGroupListView(generic.ObjectListView):
    queryset = TenantGroup.objects.add_related_count(
        TenantGroup.objects.all(),
        Tenant,
        'group',
        'tenant_count',
        cumulative=True
    )
    table = tables.TenantGroupTable


class TenantGroupView(generic.ObjectView):
    queryset = TenantGroup.objects.all()

    def get_extra_context(self, request, instance):
        tenants = Tenant.objects.restrict(request.user, 'view').filter(
            group=instance
        )

        tenants_table = tables.TenantTable(tenants)
        tenants_table.columns.hide('group')
        paginate_table(tenants_table, request)

        return {
            'tenants_table': tenants_table,
        }


class TenantGroupEditView(generic.ObjectEditView):
    queryset = TenantGroup.objects.all()
    model_form = forms.TenantGroupForm


class TenantGroupDeleteView(generic.ObjectDeleteView):
    queryset = TenantGroup.objects.all()


class TenantGroupBulkImportView(generic.BulkImportView):
    queryset = TenantGroup.objects.all()
    model_form = forms.TenantGroupCSVForm
    table = tables.TenantGroupTable


class TenantGroupBulkEditView(generic.BulkEditView):
    queryset = TenantGroup.objects.add_related_count(
        TenantGroup.objects.all(),
        Tenant,
        'group',
        'tenant_count',
        cumulative=True
    )
    filterset = filtersets.TenantGroupFilterSet
    table = tables.TenantGroupTable
    form = forms.TenantGroupBulkEditForm


class TenantGroupBulkDeleteView(generic.BulkDeleteView):
    queryset = TenantGroup.objects.add_related_count(
        TenantGroup.objects.all(),
        Tenant,
        'group',
        'tenant_count',
        cumulative=True
    )
    table = tables.TenantGroupTable


#
#  Tenants
#

class TenantListView(generic.ObjectListView):
    queryset = Tenant.objects.all()
    filterset = filtersets.TenantFilterSet
    filterset_form = forms.TenantFilterForm
    table = tables.TenantTable


class TenantView(generic.ObjectView):
    queryset = Tenant.objects.prefetch_related('group')

    def get_extra_context(self, request, instance):
        stats = {
            'site_count': Site.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'rack_count': Rack.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'rackreservation_count': RackReservation.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'device_count': Device.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'vrf_count': VRF.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'prefix_count': Prefix.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'aggregate_count': Aggregate.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'ipaddress_count': IPAddress.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'vlan_count': VLAN.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'circuit_count': Circuit.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'virtualmachine_count': VirtualMachine.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
            'cluster_count': Cluster.objects.restrict(request.user, 'view').filter(tenant=instance).count(),
        }

        return {
            'stats': stats,
        }


class TenantEditView(generic.ObjectEditView):
    queryset = Tenant.objects.all()
    model_form = forms.TenantForm


class TenantDeleteView(generic.ObjectDeleteView):
    queryset = Tenant.objects.all()


class TenantBulkImportView(generic.BulkImportView):
    queryset = Tenant.objects.all()
    model_form = forms.TenantCSVForm
    table = tables.TenantTable


class TenantBulkEditView(generic.BulkEditView):
    queryset = Tenant.objects.prefetch_related('group')
    filterset = filtersets.TenantFilterSet
    table = tables.TenantTable
    form = forms.TenantBulkEditForm


class TenantBulkDeleteView(generic.BulkDeleteView):
    queryset = Tenant.objects.prefetch_related('group')
    filterset = filtersets.TenantFilterSet
    table = tables.TenantTable
