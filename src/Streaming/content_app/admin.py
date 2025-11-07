from django.contrib import admin
from .models import Content, Playlist



class ContentAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_url', 'content_type', 'is_public', 'upload_date')

    list_filter = ('content_type', 'is_public')

    search_fields = ('title', 'description')
    ordering = ['-upload_date']


admin.site.register(Content, ContentAdmin)
admin.site.register(Playlist)