from rest_framework import serializers

from .models import CineRequest


class CineRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CineRequest
        fields = "__all__"
