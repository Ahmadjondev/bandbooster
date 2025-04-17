from django.contrib import admin
from .models import MockTest

@admin.register(MockTest)
class MockTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'test_type', 'status', 'created_at', 'overall_score')
    list_filter = ('test_type', 'status')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('id', 'created_at')
