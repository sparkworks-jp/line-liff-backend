# views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from common.exceptions import CustomAPIException
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
        raise CustomAPIException(
            status=status.HTTP_404_NOT_FOUND,
            message="商品データはまだありません",
            severity="error"
        )
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

