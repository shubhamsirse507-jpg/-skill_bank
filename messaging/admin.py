from django.contrib import admin
from .models import SkillExchange, Conversation, Message


@admin.register(SkillExchange)
class SkillExchangeAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'requester', 'receiver', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'requester__username', 'receiver__username')


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_one', 'user_two', 'created_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'conversation', 'is_read', 'created_at')
    list_filter = ('is_read',)
