import ulid
from rest_framework import serializers
from .models import UserAddress
import datetime

class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAddress
        fields = '__all__'
        extra_kwargs = {
            'address_id': {'required': False},
            'user_id': {'required': False},
        }

    def create(self, validated_data):
        # 创建新地址
        validated_data['address_id'] = ulid.new()
        validated_data['user_id'] = self.context['user_id']
        validated_data['created_at'] = validated_data['updated_at'] = datetime.datetime.now()
        validated_data['created_by'] = validated_data['updated_by'] = self.context['user_id']
        validated_data['is_default'] = False
        validated_data['deleted_flag'] = False
        return UserAddress.objects.create(**validated_data)

    def update(self, instance, validated_data):
        # 更新现有地址
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name_katakana = validated_data.get('last_name_katakana', instance.last_name_katakana)
        instance.first_name_katakana = validated_data.get('first_name_katakana', instance.first_name_katakana)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.prefecture_address = validated_data.get('prefecture_address', instance.prefecture_address)
        instance.city_address = validated_data.get('city_address', instance.city_address)
        instance.detail_address = validated_data.get('detail_address', instance.detail_address)
        instance.postal_code = validated_data.get('postal_code', instance.postal_code)
        instance.updated_at = datetime.datetime.now()
        instance.updated_by = self.context['user_id']
        instance.save()
        return instance
