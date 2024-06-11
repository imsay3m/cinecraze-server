from django.contrib import admin

from .models import CineRequest
from .views import send_cine_request_fulfilled_mail


class CineRequestAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "message", "created_at", "solved")
    list_filter = ("solved",)
    search_fields = ("name", "email", "created_at", "message")

    def save_model(self, request, obj, form, change):
        if change and "solved" in form.changed_data and obj.solved:
            # Send email notification
            send_cine_request_fulfilled_mail(obj)
        super().save_model(request, obj, form, change)


admin.site.register(CineRequest, CineRequestAdmin)
