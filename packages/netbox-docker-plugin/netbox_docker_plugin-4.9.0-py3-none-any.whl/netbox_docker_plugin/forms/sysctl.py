"""Sysctl Form definition"""

from django import forms
from utilities.forms.fields import DynamicModelChoiceField
from ..models.container import Sysctl, Container


class SysctlForm(forms.ModelForm):
    """Sysctl form definition class"""

    container = DynamicModelChoiceField(
        label="Container", queryset=Container.objects.all(), required=True
    )

    class Meta:
        """Sysctl form definition Meta class"""

        model = Sysctl
        fields = (
            "container",
            "key",
            "value",
        )
        labels = {
            "container": "Container",
            "key": "Key",
            "value": "Value",
        }
