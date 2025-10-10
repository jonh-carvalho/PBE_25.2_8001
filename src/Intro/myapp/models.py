from django.db import models

# Create your models here.
class Produto(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)
    estoque = models.IntegerField()

    def __str__(self):
        return self.nome
    
class Pedido(models.Model):
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    data_pedido = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Pedido de {self.quantidade} x {self.produto.nome}"

class Categoria(models.Model):
    nome = models.CharField(max_length=100)
    produtos = models.ManyToManyField(Produto, related_name='categorias')

    def __str__(self):
        return self.nome
    
class ProdutoDetalhe(models.Model):
    produto = models.OneToOneField(Produto, on_delete=models.CASCADE)
    detalhes = models.TextField()

    def __str__(self):
        return f"Detalhes de {self.produto.nome}"