from django.urls import path
from .views import (
    HomeView,
    StudentListView,
    StudentCreateView,
    StudentDetailView,
    StudentUpdateView,
    StudentDeleteView,
    SectionListView,
    SectionCreateView,
    SectionDeleteView,
    SectionDetailView,
    SectionUpdateView,
    GenerateSyllabusView,
)
from .class_start_views import StartSectionWizardView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('students/', StudentListView.as_view(), name='student_list'),
    path('students/add/', StudentCreateView.as_view(), name='student_add'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student_detail'),
    path('students/<int:pk>/edit/', StudentUpdateView.as_view(), name='student_edit'),
    path('students/<int:pk>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    path('sections/', SectionListView.as_view(), name='section_list'),
    path('sections/add/', SectionCreateView.as_view(), name='section_add'),
    path('sections/<int:pk>/', SectionDetailView.as_view(), name='section_detail'),
    path('sections/<int:pk>/edit/', SectionUpdateView.as_view(), name='section_edit'),
    path('sections/<int:pk>/delete/', SectionDeleteView.as_view(), name='section_delete'),
    path('sections/<int:pk>/generate_syllabus/', GenerateSyllabusView.as_view(), name='generate_syllabus'),
    path('sections/start/<int:step>/', StartSectionWizardView.as_view(), name='start_section'),

]
