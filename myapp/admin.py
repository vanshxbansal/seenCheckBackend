from django.contrib import admin
from .models import UserPost

@admin.register(UserPost)
class UserPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_at')
    search_fields = ('title',)
