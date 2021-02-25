from django.contrib import admin

# Register your models here.

from .models import *

admin.site.register(Customer)
admin.site.register(Transportation)
admin.site.register(Journey)
admin.site.register(Diet)
admin.site.register(Meal)