from django.contrib import admin
from .models import Student, Section, Lesson

# Register your models here.
admin.site.register(Student)
admin.site.register(Section)
admin.site.register(Lesson)
