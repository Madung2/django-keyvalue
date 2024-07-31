from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import KeyValue, Loan, MetaData,Template

class KeyValueAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'edited_at') 
    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'rows': 20, 'cols': 240})},
    }

class LoanAdmin(admin.ModelAdmin):
    list_display = (
        'developer', 'constructor', 'trustee', 'loan_amount', 'loan_period',
        'fee', 'irr', 'prepayment_fee', 'overdue_interest_rate', 'principal_repayment_type',
        'interest_payment_period', 'deferred_payment', 'joint_guarantee_amount',
        'lead_arranger', 'company', 'created_at'
    )

class MetaDataAdmin(admin.ModelAdmin):
    list_display = ('key', 'type', 'synonym_all', 'sp_word', 'in_use') 

admin.site.register(KeyValue, KeyValueAdmin)
admin.site.register(Loan, LoanAdmin)
admin.site.register(MetaData, MetaDataAdmin)
admin.site.register(Template)