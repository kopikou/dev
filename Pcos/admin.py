from django.contrib import admin

# Register your models here.
from .models import Patient, Ethnicity, Doctor, Appointment, Visit, Ultrasound, Laboratory_test

admin.site.register(Patient)
admin.site.register(Visit)
admin.site.register(Appointment)
admin.site.register(Ultrasound)
admin.site.register(Laboratory_test)
admin.site.register(Ethnicity)
admin.site.register(Doctor)
