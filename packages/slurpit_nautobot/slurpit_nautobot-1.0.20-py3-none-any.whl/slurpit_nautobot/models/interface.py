from django.db import models, transaction
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.urls import reverse

# Nautobot
from nautobot.extras.utils import extras_features
from nautobot.dcim.models import CableTermination, PathEndpoint, BaseInterface
from nautobot.core.models.query_functions import CollateAsChar

from nautobot.dcim.constants import (
    NONCONNECTABLE_IFACE_TYPES,
    VIRTUAL_IFACE_TYPES,
    WIRELESS_IFACE_TYPES,
)
from nautobot.core.models.fields import ForeignKeyWithAutoRelatedName, MACAddressCharField, NaturalOrderingField
from nautobot.core.models.ordering import naturalize_interface
from nautobot.core.constants import CHARFIELD_MAX_LENGTH
from nautobot.core.models.fields import ForeignKeyWithAutoRelatedName
from nautobot.core.forms import fields

from nautobot.dcim.choices import (
    InterfaceTypeChoices,
)

from nautobot.extras.models import (
    StatusField, RoleField
)
from nautobot.dcim.models.device_components import ComponentModel
from django.urls import reverse
from urllib.parse import urlencode

class InterfaceStatusField(StatusField):
    def get_limit_choices_to(self):
        """
        Limit this field to only objects which are assigned to this model's content-type.

        Note that this is implemented via specifying `content_types__app_label=` and `content_types__model=`
        rather than via the more obvious `content_types=ContentType.objects.get_for_model(self.model)`
        because the latter approach would involve a database query, and in some cases
        (most notably FilterSet definition) this function is called **before** database migrations can be run.
        """
        return {
            "content_types__app_label": "dcim",
            "content_types__model": "interface",
        }

    def formfield(self, **kwargs):
        """Return a prepped formfield for use in model forms."""
        defaults = {
            "form_class": fields.DynamicModelChoiceField,
            "queryset": self.related_model.objects.all(),
            # label_lower e.g. "dcim.device"
            "query_params": {"content_types": "dcim.interface"},
        }
        defaults.update(**kwargs)
        return super().formfield(**defaults)


class InterfaceRoleField(RoleField):
    def get_limit_choices_to(self):
        """
        Limit this field to only objects which are assigned to this model's content-type.

        Note that this is implemented via specifying `content_types__app_label=` and `content_types__model=`
        rather than via the more obvious `content_types=ContentType.objects.get_for_model(self.model)`
        because the latter approach would involve a database query, and in some cases
        (most notably FilterSet definition) this function is called **before** database migrations can be run.
        """
        return {
            "content_types__app_label": "dcim",
            "content_types__model": "interface",
        }

    def formfield(self, **kwargs):
        """Return a prepped formfield for use in model forms."""
        defaults = {
            "form_class": fields.DynamicModelChoiceField,
            "queryset": self.related_model.objects.all(),
            # label_lower e.g. "dcim.device"
            "query_params": {"content_types": "dcim.interface"},
        }
        defaults.update(**kwargs)
        return super().formfield(**defaults)
    
@extras_features(
    "custom_links",
    "custom_validators",
    "export_templates",
    "graphql",
    "statuses",
    "webhooks",
)
class SlurpitInterface(PathEndpoint, ComponentModel, BaseInterface):
    """
    A network interface within a Device. A physical Interface can connect to exactly one other Interface.
    """
     # Override ComponentModel._name to specify naturalize_interface function
    enable_reconcile = models.BooleanField(
        default=False,
        verbose_name="Enable reconcile",
    )
    status = InterfaceStatusField(blank=False, null=False)
    role = InterfaceRoleField(blank=False, null=True)
    device = ForeignKeyWithAutoRelatedName(
        to="dcim.Device", 
        on_delete=models.CASCADE, 
        null=True
    )
    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH, 
        db_index=True,
        blank=True
    )
    _name = NaturalOrderingField(
        target_field="name",
        naturalize_function=naturalize_interface,
        max_length=CHARFIELD_MAX_LENGTH,
        blank=True,
        db_index=True,
    )
    lag = models.ForeignKey(
        to="self",
        on_delete=models.SET_NULL,
        related_name="slurpit_member_interfaces",
        null=True,
        blank=True,
        verbose_name="Parent LAG",
        help_text="Assigned LAG interface",
    )
    # todoindex:
    type = models.CharField(max_length=50, choices=InterfaceTypeChoices)
    # todoindex:
    mgmt_only = models.BooleanField(
        default=False,
        verbose_name="Management only",
        help_text="This interface is used only for out-of-band management",
    )
    untagged_vlan = models.ForeignKey(
        to="ipam.VLAN",
        on_delete=models.SET_NULL,
        related_name="slurpit_interfaces_as_untagged",
        null=True,
        blank=True,
        verbose_name="Untagged VLAN",
    )
    tagged_vlans = models.ManyToManyField(
        to="ipam.VLAN",
        related_name="slurpit_interfaces_as_tagged",
        blank=True,
        verbose_name="Tagged VLANs",
    )
    vrf = models.ForeignKey(
        to="ipam.VRF",
        related_name="slurpit_interfaces",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    ignore_status = models.BooleanField(
        default=False,
        verbose_name='ignore status',
    )
    ignore_label = models.BooleanField(
        default=False,
        verbose_name='ignore label',
    )
    ignore_type = models.BooleanField(
        default=False,
        verbose_name='ignore type',
    )
    ignore_vrf = models.BooleanField(
        default=False,
        verbose_name='ignore vrf',
    )
    ignore_description = models.BooleanField(
        default=False,
        verbose_name='ignore description',
    )
    ignore_mode = models.BooleanField(
        default=False,
        verbose_name='ignore mode',
    )
    class Meta:
        ordering = ("device", CollateAsChar("_name"))
        unique_together = ("device", "name")
        verbose_name = "Slurpit Interface"
        verbose_name_plural = "Slurpit Device Interface"

    def __str__(self):
        return f"{self.name}"

    def clean(self):
        super().clean()

        # VRF validation
        if self.vrf and self.vrf not in self.device.vrfs.all():
            # TODO(jathan): Or maybe we automatically add the VRF to the device?
            raise ValidationError({"vrf": "VRF must be assigned to same Device."})

        # LAG validation
        if self.lag is not None:
            # A LAG interface cannot be its own parent
            if self.lag_id == self.pk:
                raise ValidationError({"lag": "A LAG interface cannot be its own parent."})

            # An interface's LAG must belong to the same device or virtual chassis
            if self.lag.device_id != self.device_id:
                if self.device.virtual_chassis is None:
                    raise ValidationError(
                        {
                            "lag": f"The selected LAG interface ({self.lag}) belongs to a different device ({self.lag.device})."
                        }
                    )
                elif self.lag.device.virtual_chassis_id != self.device.virtual_chassis_id:
                    raise ValidationError(
                        {
                            "lag": (
                                f"The selected LAG interface ({self.lag}) belongs to {self.lag.device}, which is not part "
                                f"of virtual chassis {self.device.virtual_chassis}."
                            )
                        }
                    )

            # A virtual interface cannot have a parent LAG
            if self.type == InterfaceTypeChoices.TYPE_VIRTUAL:
                raise ValidationError({"lag": "Virtual interfaces cannot have a parent LAG interface."})


        # Parent validation
        if self.parent_interface is not None:
            # An interface cannot be its own parent
            if self.parent_interface_id == self.pk:
                raise ValidationError({"parent_interface": "An interface cannot be its own parent."})

            # A physical interface cannot have a parent interface
            if hasattr(self, "type") and self.type != InterfaceTypeChoices.TYPE_VIRTUAL:
                raise ValidationError(
                    {"parent_interface": "Only virtual interfaces may be assigned to a parent interface."}
                )

            # An interface's parent must belong to the same device or virtual chassis
            if self.parent_interface.device != self.device:
                if getattr(self.device, "virtual_chassis", None) is None:
                    raise ValidationError(
                        {
                            "parent_interface": f"The selected parent interface ({self.parent_interface}) belongs to a different device "
                            f"({self.parent_interface.device})."
                        }
                    )
                elif self.parent_interface.device.virtual_chassis != self.device.virtual_chassis:
                    raise ValidationError(
                        {
                            "parent_interface": f"The selected parent interface ({self.parent_interface}) belongs to {self.parent_interface.device}, which "
                            f"is not part of virtual chassis {self.device.virtual_chassis}."
                        }
                    )



    @property
    def is_connectable(self):
        return self.type not in NONCONNECTABLE_IFACE_TYPES

    @property
    def is_virtual(self):
        return self.type in VIRTUAL_IFACE_TYPES

    @property
    def is_wireless(self):
        return self.type in WIRELESS_IFACE_TYPES

    @property
    def is_lag(self):
        return self.type == InterfaceTypeChoices.TYPE_LAG

    @property
    def parent(self):
        return self.device

    def get_absolute_url(self):
        base_url = reverse("plugins:slurpit_nautobot:reconcile_list")
        query_params = {'tab': "interface", "pk": self.pk}
        # Encode your query parameters and append them to the base URL
        url_with_querystring = f"{base_url}?{urlencode(query_params)}"

        return url_with_querystring
        # return reverse('plugins:slurpit_nautobot:reconcile_detail', args=[self.pk, 'interface'])
    
    def get_edit_url(self):
        query_params = {'tab': "interface"}
        base_url = reverse("plugins:slurpit_nautobot:reconcile_list")
        # Encode your query parameters and append them to the base URL
        url_with_querystring = f"{base_url}?{urlencode(query_params)}"

        base_url = reverse('plugins:slurpit_nautobot:slurpitinterface_edit', args=[self.pk])
        query_params = {'return_url': url_with_querystring}
        url_with_querystring = f"{base_url}?{urlencode(query_params)}"

        return url_with_querystring