from django.contrib import admin
from flatblocks.models import FlatBlock


class FlatBlockAdmin(admin.ModelAdmin):
    ordering = ['slug', ]
    list_display = ('slug', 'header', 'site', )
    list_filter = ('site', )
    search_fields = ('slug', 'header', 'content', 'site__domain', 'site__name', )

admin.site.register(FlatBlock, FlatBlockAdmin)
