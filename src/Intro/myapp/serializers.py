# minhaapp/serializers.py
from rest_framework import serializers
from myapp.models import Produto, Pedido, Categoria, ProdutoDetalhe

class ProdutoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Produto
        fields = ['id', 'nome', 'preco', 'descricao', 'estoque']

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ['id', 'produto', 'quantidade', 'data_pedido']

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nome', 'produtos']

class ProdutoDetalheSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProdutoDetalhe
        fields = ['id', 'produto', 'detalhes']
        read_only_fields = ['id']

