from django.urls import path, include
# from django.conf.urls import url
from . import viewset
from rest_framework import routers
# from rest_framework_simplejwt.views import TokenVerifyView, TokenObtainPairView, TokenRefreshView

router = routers.DefaultRouter()
router.register('dremio_catalog', viewset.CatalogViewset, basename='dremio_catalog')
router.register('dremio_dataset', viewset.DatasetViewset, basename='dremio_dataset')
router.register('dremio_reflection', viewset.ReflectionViewset, basename='dremio_reflection')

app_name = 'dremio'

urlpatterns = [
    # RESTAPI
    path('api/', include(router.urls)),
    # path('api/gettoken/', TokenObtainPairView.as_view(), name='gettoken'),
    # path('api/refreshtoken/', TokenRefreshView.as_view(), name='refreshtoken'),
    # path('api/verifytoken/', TokenVerifyView.as_view(), name='verifytoken'),

    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # MAIN PAGE
    # path('', views.main, name='main'),
    # # APP 1
    # path('alert_list/', views.alert_detail, name='alert_detail'),
    # OTHERS

]
