# serializers.py
from rest_framework import serializers
from .models import Product
import logging

logger = logging.getLogger(__name__)

class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = '__all__'
