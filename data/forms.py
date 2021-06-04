from django.forms import ModelForm
from data.models import AlertRule

class AlertRuleForm(ModelForm):
    
    class Meta:
        model = AlertRule
        fields = '__all__'
