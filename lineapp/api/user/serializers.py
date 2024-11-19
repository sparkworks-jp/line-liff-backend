from rest_framework import serializers
from .models import User, UserAddress
import ulid


class UserSerializer(serializers.ModelSerializer):
    """ユーザー情報シリアライザー"""
    class Meta:
        model = User
        fields = [
            'id', 'line_user_id', 'mail', 'user_name', 'role',
            'birthday', 'gender', 'phone_number',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'line_user_id', 'role', 'created_at', 'updated_at']

class UserAddressSerializer(serializers.ModelSerializer):
    """ユーザー住所シリアライザー"""
    class Meta:
        model = UserAddress
        fields = [
            'address_id', 'user_id', 'last_name', 'first_name',
            'last_name_katakana', 'first_name_katakana',
            'phone_number', 'prefecture_address', 'city_address',
            'district_address', 'detail_address', 'postal_code',
            'is_default', 'created_at', 'updated_at'
        ]
        read_only_fields = ['address_id', 'created_at', 'updated_at']

    def create(self, validated_data):
        # アドレスID生成
        validated_data['address_id'] = str(ulid.new())
        
        # デフォルト住所の処理
        if validated_data.get('is_default'):
            # 既存のデフォルト住所をfalseに設定
            UserAddress.objects.filter(
                user_id=validated_data['user_id'],
                is_default=True
            ).update(is_default=False)
            
        return super().create(validated_data)

    def update(self, instance, validated_data):
        # デフォルト住所の処理
        if validated_data.get('is_default'):
            # 既存のデフォルト住所をfalseに設定
            UserAddress.objects.filter(
                user_id=instance.user_id,
                is_default=True
            ).exclude(address_id=instance.address_id).update(is_default=False)
            
        return super().update(instance, validated_data)

# 検証用シリアライザー
class AddressCreateValidator(serializers.Serializer):
    """住所作成バリデーター"""
    last_name = serializers.CharField(max_length=50)
    first_name = serializers.CharField(max_length=50)
    last_name_katakana = serializers.CharField(max_length=50)
    first_name_katakana = serializers.CharField(max_length=50)
    phone_number = serializers.CharField(max_length=50)
    prefecture_address = serializers.CharField(max_length=255)
    city_address = serializers.CharField(max_length=255)
    district_address = serializers.CharField(max_length=255, required=False, allow_null=True)
    detail_address = serializers.CharField(max_length=255)
    postal_code = serializers.CharField(max_length=50)
    is_default = serializers.BooleanField(default=False)