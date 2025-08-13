"""
Admin site customization for sk-com project.
"""

from django.contrib import admin
from django.contrib.admin import AdminSite

# Customize the admin site headers
admin.site.site_header = "SK Portfolio Administration"
admin.site.site_title = "SK Admin"
admin.site.index_title = "Welcome to SK Portfolio Admin"
