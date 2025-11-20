from nautobot.extras.utils import extras_features
from nautobot.core.models.generics import PrimaryModel
from nautobot.core.constants import CHARFIELD_MAX_LENGTH
from nautobot.extras.models import RoleField, StatusField
from nautobot.core.models import BaseManager
from nautobot.ipam.querysets import VLANQuerySet
from nautobot.core.forms import fields

from django.db import models, transaction
from django.core.validators import MaxValueValidator, MinValueValidator
from urllib.parse import urlencode
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class VLANStatusField(StatusField):
    def get_limit_choices_to(self):
        """
        Limit this field to only objects which are assigned to this model's content-type.

        Note that this is implemented via specifying `content_types__app_label=` and `content_types__model=`
        rather than via the more obvious `content_types=ContentType.objects.get_for_model(self.model)`
        because the latter approach would involve a database query, and in some cases
        (most notably FilterSet definition) this function is called **before** database migrations can be run.
        """
        return {
            "content_types__app_label": "ipam",
            "content_types__model": "vlan",
        }

    def formfield(self, **kwargs):
        """Return a prepped formfield for use in model forms."""
        defaults = {
            "form_class": fields.DynamicModelChoiceField,
            "queryset": self.related_model.objects.all(),
            # label_lower e.g. "dcim.device"
            "query_params": {"content_types": "ipam.vlan"},
        }
        defaults.update(**kwargs)
        return super().formfield(**defaults)

class VLANRoleField(RoleField):
    def get_limit_choices_to(self):
        """
        Limit this field to only objects which are assigned to this model's content-type.

        Note that this is implemented via specifying `content_types__app_label=` and `content_types__model=`
        rather than via the more obvious `content_types=ContentType.objects.get_for_model(self.model)`
        because the latter approach would involve a database query, and in some cases
        (most notably FilterSet definition) this function is called **before** database migrations can be run.
        """
        return {
            
            "content_types__app_label": "ipam",
            "content_types__model": "vlan",
        }

    def formfield(self, **kwargs):
        """Return a prepped formfield for use in model forms."""
        defaults = {
            "form_class": fields.DynamicModelChoiceField,
            "queryset": self.related_model.objects.all(),
            # label_lower e.g. "dcim.device"
            "query_params": {"content_types": "ipam.vlan"},
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
class SlurpitVLAN(PrimaryModel):
    """
    A VLAN is a distinct layer two forwarding domain identified by a 12-bit integer (1-4094).
    Each VLAN must be assigned to a Location, however VLAN IDs need not be unique within a Location.
    A VLAN may optionally be assigned to a VLANGroup, within which all VLAN IDs and names but be unique.

    Like Prefixes, each VLAN is assigned an operational status and optionally a user-defined Role. A VLAN can have zero
    or more Prefixes assigned to it.
    """
    vlan_group = models.CharField(
        verbose_name=_('vlan group'),
        max_length=64,
        blank=True,
        null=True,
    )
    vid = models.PositiveSmallIntegerField(
        verbose_name="ID", validators=[MinValueValidator(1), MaxValueValidator(4094)]
    )
    name = models.CharField(
        max_length=CHARFIELD_MAX_LENGTH, 
        db_index=True,
        default = _(''),
        blank=True,
        null=True
    )
    status = VLANStatusField(blank=False, null=False)
    role = VLANRoleField(blank=True, null=True)
    tenant = models.ForeignKey(
        to="tenancy.Tenant",
        on_delete=models.PROTECT,
        related_name="slurpit_vlans",
        blank=True,
        null=True,
    )
    description = models.CharField(max_length=CHARFIELD_MAX_LENGTH, blank=True)

    enable_reconcile = models.BooleanField(
        default=False,
        verbose_name=_('enable reconcile'),
    )    
    ignore_status = models.BooleanField(
        default=False,
        null=True,
        verbose_name=_('ignore status'),
    )
    ignore_vid = models.BooleanField(
        default=False,
        null=True,
        verbose_name=_('ignore vid'),
    )
    ignore_role = models.BooleanField(
        default=False,
        null=True,
        verbose_name=_('ignore role'),
    )
    ignore_tenant = models.BooleanField(
        default=False,
        null=True,
        verbose_name=_('ignore tenant'),
    )
    ignore_description = models.BooleanField(
        default=False,
        null=True,
        verbose_name=_('ignore description'),
    )


    clone_fields = [
        "vlan_group",
        "tenant",
        "status",
        "role",
        "description",
    ]

    natural_key_field_names = ["pk"]
    objects = BaseManager.from_queryset(VLANQuerySet)()

    class Meta:
        ordering = (
            "vlan_group",
            "vid",
        )  # (location, group, vid) may be non-unique
        unique_together = [
            # 2.0 TODO: since group is nullable and NULL != NULL, we can have multiple non-group VLANs with
            # the same vid and name. We should probably fix this with a custom validate_unique() function.
            ["vlan_group", "vid"],
            ["vlan_group", "name"],
        ]
        verbose_name = "Slurpit VLAN"
        verbose_name_plural = "Slurpit VLANs"

    def __str__(self):
        return self.display or super().__str__()

    def __init__(self, *args, **kwargs):
        # TODO: Remove self._location, location @property once legacy `location` field is no longer supported
        super().__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        # Using atomic here cause legacy `location` is inserted into `locations`() which might result in an error.
        with transaction.atomic():
            super().save(*args, **kwargs)

    @property
    def display(self):
        return f"{self.name} ({self.vid})"

    def get_edit_url(self):
        query_params = {'tab': "vlan"}
        base_url = reverse("plugins:slurpit_nautobot:reconcile_list")
        # Encode your query parameters and append them to the base URL
        url_with_querystring = f"{base_url}?{urlencode(query_params)}"

        base_url = reverse('plugins:slurpit_nautobot:slurpitvlan_edit', args=[self.pk])
        query_params = {'return_url': url_with_querystring}
        url_with_querystring = f"{base_url}?{urlencode(query_params)}"

        return url_with_querystring
    
    def get_absolute_url(self):
        return reverse('plugins:slurpit_nautobot:reconcile_detail', args=[self.pk, 'vlan'])