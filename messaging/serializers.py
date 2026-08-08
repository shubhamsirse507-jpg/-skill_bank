"""
messaging/serializers.py
DRF serializers for SkillExchange, Conversation, Message.
"""
from rest_framework import serializers
from .models import SkillExchange, Conversation, Message


class SkillExchangeSerializer(serializers.ModelSerializer):
    requester_username = serializers.CharField(source='requester.username', read_only=True)
    receiver_username = serializers.CharField(source='receiver.username', read_only=True)
    skill_name = serializers.CharField(source='skill.name', read_only=True)

    class Meta:
        model = SkillExchange
        fields = [
            'id', 'requester', 'requester_username', 'receiver', 'receiver_username',
            'skill', 'skill_name', 'title', 'message', 'status', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'requester']


class MessageSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)

    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_username',
            'message_text', 'is_read', 'has_attachment', 'attachment_name', 'created_at',
        ]
        read_only_fields = ['id', 'sender', 'created_at']


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    user_one_username = serializers.CharField(source='user_one.username', read_only=True)
    user_two_username = serializers.CharField(source='user_two.username', read_only=True)

    class Meta:
        model = Conversation
        fields = [
            'id', 'request', 'user_one', 'user_one_username',
            'user_two', 'user_two_username', 'created_at', 'messages',
        ]
        read_only_fields = ['id', 'created_at']
