import os
from django.http import HttpResponse
from django.views.generic import View
from django.conf import settings
from django.views.static import serve

# Vue 静态文件根目录
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static", "ui")


class SwaggerView(View):
    """返回 Vue 打包的 index.html"""

    def get(self, request):
        with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
            html = f.read()
        return HttpResponse(html)


class SwaggerStaticView(View):
    """提供 Vue 静态资源访问（CSS/JS）"""

    def get(self, request, path):
        return serve(request, path, document_root=os.path.join(STATIC_DIR, "assets"))
