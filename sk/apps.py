from django.apps import AppConfig
from django.contrib import admin


class SkConfig(AppConfig):
    name = 'sk'
    verbose_name = 'SK Portfolio'

    def ready(self):
        # Customize the admin site headers
        admin.site.site_header = "SK Portfolio Administration"
        admin.site.site_title = "SK Admin"
        admin.site.index_title = "Welcome to SK Portfolio Admin"
