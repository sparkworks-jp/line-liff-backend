# serializers.py

from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'
    
    def get_image(self, obj):
        if obj.image:
            if str(obj.image).startswith('https://'):
                return str(obj.image)
            return f"https://line-liff-app.s3.ap-northeast-1.amazonaws.com/public/{str(obj.image).lstrip('/')}"
        return None
