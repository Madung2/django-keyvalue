from django.contrib import admin
from django.db import models
from django.forms import Textarea
from .models import KeyValue

class KeyValueAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'edited_at') 
    formfield_overrides = {
        models.JSONField: {'widget': Textarea(attrs={'rows': 20, 'cols': 240})},
    }

admin.site.register(KeyValue, KeyValueAdmin)