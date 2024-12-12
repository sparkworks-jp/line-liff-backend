from rest_framework import serializers
from .models import User, UserAddress


class UserSerializer(serializers.ModelSerializer):
    """ユーザー情報シリアライザー"""
    class Meta:
        model = User
        fields = [
            'user_id', 'line_user_id', 'mail', 'user_name', 'role',
            'birthday', 'gender', 'phone_number',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'line_user_id', 'role', 'created_at', 'updated_at']

class UserAddressSerializer(serializers.ModelSerializer):
    """ユーザー住所シリアライザー"""
    prefecture_address_id = serializers.IntegerField(write_only=True, required=True) 
    prefecture_address = serializers.CharField(read_only=True)

    
    class Meta:
        model = UserAddress
        fields = [
            'address_id', 'user_id', 'last_name', 'first_name',
            'last_name_katakana', 'first_name_katakana',
            'phone_number', 'prefecture_address', 'prefecture_address_id',
            'city_address', 'district_address', 'detail_address',
            'postal_code', 'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['address_id', 'user_id', 'created_at', 'updated_at']

