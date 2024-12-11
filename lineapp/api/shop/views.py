# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from common.constants import SaleStatus


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
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

