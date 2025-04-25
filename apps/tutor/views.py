from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, RedirectView, UpdateView, FormView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Student, Section
from .forms import StudentForm, SectionForm
from django.views import View
from django.contrib import messages


class HomeView(TemplateView):
    template_name = "home.html"


class StudentListView(LoginRequiredMixin, ListView):
    model = Student
    template_name = 'students/student_list.html'
    context_object_name = 'students'

    def get_queryset(self):
        return Student.objects.filter(tutor=self.request.user)


class StudentCreateView(LoginRequiredMixin, CreateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')

    def form_valid(self, form):
        form.instance.tutor = self.request.user
        return super().form_valid(form)


class StudentDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Student
    template_name = 'students/student_detail.html'
    context_object_name = 'student'

    def test_func(self):
        return self.get_object().tutor == self.request.user


class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'students/student_form.html'
    success_url = reverse_lazy('student_list')

    def test_func(self):
        return self.get_object().tutor == self.request.user


class StudentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Student
    template_name = 'students/student_confirm_delete.html'
    success_url = reverse_lazy('student_list')

    def test_func(self):
        return self.get_object().tutor == self.request.user


class SectionListView(LoginRequiredMixin, ListView):
    model = Section
    template_name = 'sections/section_list.html'
    context_object_name = 'sections'

    def get_queryset(self):
        return Section.objects.filter(tutor=self.request.user)


class SectionCreateView(LoginRequiredMixin, CreateView):
    model = Section
    form_class = SectionForm
    template_name = 'sections/section_form.html'

    def get_success_url(self):
        return reverse_lazy('section_detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.tutor = self.request.user
        section = form.save(commit=False)

        # Generate syllabus during creation only
        section.generate_syllabus()
        form.save_m2m()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create_view'] = True
        return context


class SectionDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Section
    template_name = 'sections/section_detail.html'
    context_object_name = 'section'

    def test_func(self):
        return self.get_object().tutor == self.request.user


class SectionUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Section
    form_class = SectionForm
    template_name = 'sections/section_form.html'

    def get_success_url(self):
        return reverse_lazy('section_detail', kwargs={'pk': self.object.pk})

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.tutor = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.get_object().tutor == self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_create_view'] = False
        return context


class SectionDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Section
    template_name = 'sections/section_confirm_delete.html'
    success_url = reverse_lazy('section_list')

    def test_func(self):
        return self.get_object().tutor == self.request.user


class GenerateSyllabusView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        section = get_object_or_404(Section, pk=pk)

        # Basic check to make sure the user owns the section
        if section.tutor != request.user:
            return self.handle_no_permission()

        section.generate_syllabus()
        messages.success(request, "Syllabus generated!")

        return redirect('section_detail', pk=pk)

    def test_func(self):
        section = get_object_or_404(Section, pk=self.kwargs['pk'])
        return section.tutor == self.request.user
