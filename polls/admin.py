from django.contrib import admin

from polls.models import Option, Poll


class OptionAdminInline(admin.TabularInline):
    model = Option
    extra = 1


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    inlines = (OptionAdminInline,)
