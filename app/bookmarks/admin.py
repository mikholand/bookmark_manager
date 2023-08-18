from django.contrib import admin

from .models import Bookmark, Collection

admin.site.register(Bookmark)
admin.site.register(Collection)
