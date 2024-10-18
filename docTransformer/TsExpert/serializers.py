from rest_framework import serializers
from django.forms.models import model_to_dict
# from .models import Rules



# class RulesSerializer(serializers.ModelSerializer):
#     types = serializers.SerializerMethodField()
#     def get_types(self, instance):
#         """
#         Returns the main contract type for a given Rules instance.
#         """
#         # Convert the model instance to a dictionary
#         model_dict = model_to_dict(instance)

#         # Remove unwanted fields and exclude fields with None values or empty strings
#         excluded_fields = ['id', 'template_idx', 'final_text', 'highlight']
#         model_dict = {
#             key: value
#             for key, value in model_dict.items()
#             if key not in excluded_fields and (value is not None and value != '')
#         }

#         return model_dict

#     def to_representation(self, instance):
#         """
#         Object instance -> Dict of primitive datatypes.
#         """
#         ret = super().to_representation(instance)
#         # Filter out any key-value pairs where the value is None
#         ret = {key: value for key, value in ret.items() if value is not None}
    
#         return ret

#     class Meta:
#         model = Rules
#         fields = ['id', 'template_idx', 'final_text', 'types', 'highlight']
