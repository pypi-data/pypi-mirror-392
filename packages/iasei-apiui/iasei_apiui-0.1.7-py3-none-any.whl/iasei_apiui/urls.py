from django.urls import path, re_path
from .views import SwaggerView, SwaggerStaticView

urlpatterns = [
    # Swagger UI 入口
    path("", SwaggerView.as_view(), name="swagger-ui"),
    # 静态资源路由（匹配 CSS/JS 等）
    re_path(r"^assets/(?P<path>.*)$", SwaggerStaticView.as_view(), name="swagger-static"),
]
