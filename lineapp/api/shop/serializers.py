# serializers.py
from rest_framework import serializers
from .models import Product
import logging

logger = logging.getLogger(__name__)

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
    
    def get_image(self, obj):
        if not obj.image:
            return None            
        image_url = str(obj.image)
        if image_url.startswith(('https://', 'http://')):
            return image_url       
        logger.warning(f"予期しないイメージURLの形式です: {image_url}")
        return image_url
