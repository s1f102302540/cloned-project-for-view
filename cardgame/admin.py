from django.contrib import admin
from .models import Card, CardEffect, Session, Player

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost')

@admin.register(CardEffect)
class CardEffectAdmin(admin.ModelAdmin):
    list_display = ('card', 'effect_type', 'target_type')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'is_active', 'current_turn')

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'session', 'health', 'mana', 'is_active')
