# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import APIException

from common.exceptions import CustomAPIException
from .models import Product
from .serializers import ProductSerializer
from django.shortcuts import get_object_or_404
from common.constants import SaleStatus

@api_view(['GET'])
def get_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    if not product.is_active:
        raise CustomAPIException(
            status=status.HTTP_404_NOT_FOUND,
            message="商品已下架",
            severity="warning"
        )
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view(['GET'])
def list_products(request):
    products = Product.objects.filter(
        sale_status=SaleStatus.ON_SALE, 
        deleted_flag=False 
    )
    if not products.exists():
        return Response({
            'message': '商品データはまだありません',
            'data': []
        }, status=status.HTTP_200_OK)
    print("image值:", products.first().image)
    serializer = ProductSerializer(products, many=True)
    print("シリアル化image值:", serializer.data[0]['image'])

    return Response(serializer.data)

