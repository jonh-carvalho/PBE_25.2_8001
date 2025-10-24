# 16 - **Regras de negócio**

---

## Regras de Negócio

1. **Cada conteúdo deve ter uma miniatura (`thumbnail_url`) e uma descrição.**
2. **O título deve ser único por criador (`User`).**

---

## Modelo `Content` com validações

```python
# models.py
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

class Content(models.Model):
    CONTENT_TYPE_CHOICES = (
        ('audio', 'Áudio'),
        ('video', 'Vídeo'),
    )

    title = models.CharField(max_length=255)
    description = models.TextField()
    file_url = models.URLField()
    thumbnail_url = models.URLField()
    content_type = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contents')

    def clean(self):
        # Regra 1: Descrição e miniatura obrigatórias
        if not self.description:
            raise ValidationError("Descrição é obrigatória.")
        if not self.thumbnail_url:
            raise ValidationError("Miniatura (thumbnail) é obrigatória.")

        # Regra 2: Título único por criador
        existing = Content.objects.filter(title=self.title, creator=self.creator)
        if self.pk:
            existing = existing.exclude(pk=self.pk)
        if existing.exists():
            raise ValidationError("Você já criou um conteúdo com este título.")

    def save(self, *args, **kwargs):
        self.full_clean()  # Chama `clean()` automaticamente antes de salvar
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.content_type})"
```

---

## O que acontece com essas regras?

* Se um usuário tentar **salvar um conteúdo sem descrição ou sem miniatura**, ele receberá um erro.
* Se um mesmo criador tentar cadastrar **dois conteúdos com o mesmo título**, receberá erro de validação.

---

Se estiver usando `ModelSerializer` no Django REST Framework, ele também vai capturar e retornar essas validações automaticamente como mensagens de erro no `POST` ou `PUT`.

Perfeito! Abaixo está a adaptação das **regras de negócio** diretamente no `serializer` do **Django REST Framework**, para garantir:

* Que `description` e `thumbnail_url` sejam obrigatórios.
* Que o `title` seja único **por criador (user)**.

---

## `serializers.py` com validações personalizadas

```python
# serializers.py
from rest_framework import serializers
from .models import Content

class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Content
        fields = '__all__'
        read_only_fields = ['owner', 'created_at']

    def validate(self, data):
        # Regra: descrição e miniatura obrigatórias
        if not data.get('description'):
            raise serializers.ValidationError({"description": "Descrição é obrigatória."})

        if not data.get('thumbnail_url'):
            raise serializers.ValidationError({"thumbnail_url": "Miniatura é obrigatória."})

        # Regra: título único por criador
        request = self.context.get('request')
        owner = request.user if request else None
        title = data.get('title')

        if self.instance:
            # Atualização: ignora o próprio objeto
            exists = Content.objects.filter(title=title, owner=owner).exclude(pk=self.instance.pk).exists()
        else:
            exists = Content.objects.filter(title=title, owner=owner).exists()

        if exists:
            raise serializers.ValidationError({"title": "Você já possui um conteúdo com esse título."})

        return data

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
```

---

## O que foi feito:

* O método `validate` trata múltiplos campos ao mesmo tempo.
* `request.user` é usado como o criador (owner).
* O `create` já insere o `owner` automaticamente com base no usuário logado.
* Campos `owner` e `created_at` são **somente leitura** (`read_only_fields`).

---

## Exemplo de `views.py`

```python
# views.py
from rest_framework import viewsets, permissions
from .models import Content
from .serializers import ContentSerializer

class ContentViewSet(viewsets.ModelViewSet):
    queryset = Content.objects.all()
    serializer_class = ContentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
```

---

### Django Admin

Agora temos as regras no **admin Django** para reforçar a validação em múltiplos pontos, garantindo uma camada adicional de validação para:

1. **Miniatura (`thumbnail_url`) e descrição obrigatórias.**
2. **Título único por criador.**

---

## 1. Adicionar validações no `ModelAdmin`

```python
# admin.py
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms import ModelForm
from .models import Content

class ContentAdminForm(ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get("title")
        owner = cleaned_data.get("owner")

        # Validação: descrição e miniatura
        if not cleaned_data.get("description"):
            raise ValidationError("Descrição é obrigatória.")
        if not cleaned_data.get("thumbnail_url"):
            raise ValidationError("Miniatura (thumbnail) é obrigatória.")

        # Validação: título único por criador
        qs = Content.objects.filter(title=title, owner=owner)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Esse criador já possui um conteúdo com esse título.")

        return cleaned_data

class ContentAdmin(admin.ModelAdmin):
    form = ContentAdminForm
    list_display = ['title', 'owner', 'content_type', 'created_at']
    list_filter = ['content_type', 'owner']
    search_fields = ['title', 'description']

admin.site.register(Content, ContentAdmin)
```

---

### 2. Benefícios dessas validações no Admin

* Garante que **mesmas regras aplicadas na API também valem no admin**.
* O admin exibe mensagens amigáveis quando há erros.
* Ajuda a prevenir inconsistências se alguém usar apenas o admin.

---

Se você quiser, posso mostrar como adicionar **permissões específicas** no admin para controlar quem pode ver, editar ou excluir conteúdos. Deseja seguir com isso?

### Playlist

A seguir temos as **regras de negócio para a entidade `Playlist`** no seu app Django REST.
As regras são:

---

### Regras de Negócio

1. **Título único por usuário** — o nome da playlist deve ser único para cada criador.
2. **Conteúdos não podem ser duplicados dentro de uma mesma playlist.**

---

## MODELO (`models.py`)

```python
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Content  # supondo que Content já exista

class Playlist(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='playlists')
    contents = models.ManyToManyField(Content, related_name='playlists', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('title', 'owner')
        ordering = ['-created_at']

    def clean(self):
        # Regra 1: título único já garantido pelo unique_together
        pass  # Regras adicionais podem ser adicionadas aqui

    def __str__(self):
        return f"{self.title} - {self.owner.username}"
```

---

## SERIALIZER (`serializers.py`)

```python
from rest_framework import serializers
from .models import Playlist, Content

class PlaylistSerializer(serializers.ModelSerializer):
    contents = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Content.objects.all(), required=False
    )

    class Meta:
        model = Playlist
        fields = ['id', 'title', 'owner', 'contents', 'created_at']
        read_only_fields = ['owner', 'created_at']

    def validate_title(self, value):
        user = self.context['request'].user
        if Playlist.objects.filter(title=value, owner=user).exists():
            raise serializers.ValidationError("Você já tem uma playlist com esse título.")
        return value

    def validate_contents(self, value):
        if len(value) != len(set(value)):
            raise serializers.ValidationError("A playlist não pode conter conteúdos duplicados.")
        return value

    def create(self, validated_data):
        contents = validated_data.pop('contents', [])
        playlist = Playlist.objects.create(owner=self.context['request'].user, **validated_data)
        playlist.contents.set(contents)
        return playlist

    def update(self, instance, validated_data):
        contents = validated_data.pop('contents', None)
        if contents is not None:
            if len(contents) != len(set(contents)):
                raise serializers.ValidationError("A playlist não pode conter conteúdos duplicados.")
            instance.contents.set(contents)
        return super().update(instance, validated_data)
```

---

## VIEWS (`views.py`)

```python
from rest_framework import viewsets, permissions
from .models import Playlist
from .serializers import PlaylistSerializer

class PlaylistViewSet(viewsets.ModelViewSet):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Apenas as playlists do usuário autenticado
        return Playlist.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
```

---

## URLs (`urls.py`)

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlaylistViewSet

router = DefaultRouter()
router.register(r'playlists', PlaylistViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

---

## DJANGO ADMIN (`admin.py`)

```python
from django.contrib import admin
from .models import Playlist

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created_at')
    list_filter = ('owner',)
    search_fields = ('title',)
    filter_horizontal = ('contents',)

    def save_model(self, request, obj, form, change):
        # Força o owner no admin
        if not obj.pk:
            obj.owner = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Playlist, PlaylistAdmin)
```

---

## Resultado

* **Playlists com nomes únicos por usuário.**
* **Conteúdos duplicados são rejeitados.**
* Funciona no **admin**, **API REST**, **serializers**, **validações automáticas**.
