from django.contrib import admin
from .models import Produto, Pedido, Categoria, ProdutoDetalhe


# Register your models here.
admin.site.register(Produto)
admin.site.register(Pedido)
admin.site.register(Categoria)
admin.site.register(ProdutoDetalhe)
