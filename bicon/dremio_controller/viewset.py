from rest_framework import viewsets
from .serializers import *
from .models import *
from rest_framework.permissions import IsAuthenticated, IsAdminUser
# from rest_framework_simplejwt.views import TokenVerifyView, TokenObtainPairView, TokenRefreshView
# from rest_framework_simplejwt.authentication import JWTAuthentication


class CatalogViewset(viewsets.ModelViewSet):
    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer
    # permission_classes = [IsAuthenticated]
    # authentication_classes = [JWTAuthentication]


class DatasetViewset(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer
    # permission_classes = [IsAdminUser]
    # authentication_classes = [JWTAuthentication]


class ReflectionViewset(viewsets.ModelViewSet):
    queryset = Reflection.objects.all()
    serializer_class = ReflectionSerializer
    # permission_classes = [IsAdminUser]
    # authentication_classes = [JWTAuthentication]
