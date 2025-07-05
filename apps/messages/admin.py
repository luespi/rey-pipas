from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Thread, Message


@admin.register(Thread)
class ThreadAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "created_at")
    list_filter  = ("order",)
    search_fields = ("order__id",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display  = ("id", "thread", "sender", "created_at")
    list_filter   = ("sender", "thread")
    search_fields = ("text",)
    readonly_fields = ("created_at",)
