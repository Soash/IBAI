from django.contrib import admin
from payments.models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'tran_id', 'amount', 'status', 'created_at')
    search_fields = ('user__username', 'course__title', 'tran_id')
    list_filter = ('status', 'created_at')
    readonly_fields = ('created_at',)

