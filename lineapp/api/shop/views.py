# views.py

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Product
from .serializers import ProductSerializer
from django.shortcuts import get_object_or_404
from core.middleware.line_auth import line_auth_required

# @api_view(['POST'])
# def create_product(request):
#     serializer = ProductSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_product(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    serializer = ProductSerializer(product)
    return Response(serializer.data)

@api_view(['GET'])
@line_auth_required
def list_products(request):
    products = Product.objects.all()
    print("原始image值:", products.first().image)
    serializer = ProductSerializer(products, many=True)
    print("序列化后image值:", serializer.data[0]['image'])

    return Response(serializer.data)

# @api_view(['PUT'])
# def update_product(request, product_id):
#     product = get_object_or_404(Product, product_id=product_id)
#     serializer = ProductSerializer(product, data=request.data, partial=True)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# @api_view(['DELETE'])
# def delete_product(request, product_id):
#     product = get_object_or_404(Product, product_id=product_id)
#     product.delete()
#     return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
