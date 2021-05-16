from django.db import models
from django.db.models import fields
from rest_framework import serializers
from rest_framework.fields import empty

class CustomModelSerializer(serializers.ModelSerializer):
    translate_fields = []

    def __init__(self, instance=None, data=None, extra_data={}, **kwargs):
        self.hide_serializer_fields = kwargs.pop('hide_serializer_fields', False)
        if self.hide_serializer_fields:
            self.remove_serializer_fields(**kwargs)
        
        json_data = {}
        if data:
            for key in data:
                value = data.get(key, None)
                json_data[key] = value
        json_data.update(extra_data)

        super().__init__(instance=instance, data=(json_data or empty), **kwargs)
    
    def remove_serializer_fields(self, **kwargs):
        serializer_fields = []
        for field_name in self.fields:
            if isinstance(self.fields[field_name], serializers.BaseSerializer):
                serializer_fields.append(field_name)
        for field_name in serializer_fields:
            self.fields.pop(field_name, None)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        for field_name in self.translate_fields:
            translated_value = ret.get(field_name + '_hi')
            if translated_value:
                ret[field_name] = translated_value
        return ret