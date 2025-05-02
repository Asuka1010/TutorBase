from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView, RedirectView, UpdateView, FormView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from .models import Student, Section, Lesson
from .forms import StudentForm, SectionForm, LessonStep1Form, LessonStep2Form, LessonForm
from django.views import View
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            context['sections'] = Section.objects.filter(tutor=self.request.user)

            today = timezone.localtime().date()
            year = int(self.request.GET.get('year', today.year))
            month = int(self.request.GET.get('month', today.month))
            selected_date_str = self.request.GET.get('date')
            selected_date = datetime.strptime(selected_date_str, "%Y-%m-%d").date() if selected_date_str else today

            # Month metadata
            context['year'] = year
            context['month'] = month
            context['calendar_month_name'] = datetime(year, month, 1).strftime('%B %Y')

            # Lessons
            lessons = Lesson.objects.filter(
                section__tutor=self.request.user,
                date__year=year,
                date__month=month
            )

            # Lessons for selected date
            context['selected_date'] = selected_date
            context['lessons_for_selected_day'] = Lesson.objects.filter(
                section__tutor=self.request.user,
                date__date=selected_date
            ).order_by('date')

            # Build calendar grid (weeks of [date, is_current_month, has_lessons])
            first_of_month = datetime(year, month, 1).date()
            start_day = first_of_month - timedelta(days=first_of_month.weekday() + 1 if first_of_month.weekday() != 6 else 0)
            calendar_days = []
            for week in range(6):
                week_days = []
                for day in range(7):
                    date = start_day + timedelta(days=week * 7 + day)
                    has_event = lessons.filter(date__date=date).exists()
                    week_days.append({
                        'date': date,
                        'in_current_month': date.month == month,
                        'is_today': date == today,
                        'has_event': has_event,
                    })
                calendar_days.append(week_days)

            context['calendar_weeks'] = calendar_days

        return context


class CalendarPartialView(LoginRequiredMixin, View):
    def get(self, request):
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))

        today = timezone.localtime().date()
        lessons = Lesson.objects.filter(
            section__tutor=request.user,
            date__year=year,
            date__month=month
        )

        lessons_by_day = {}
        for lesson in lessons:
            lessons_by_day.setdefault(lesson.date.day, []).append(lesson)

        calendar_weeks = get_calendar_weeks(year, month)

        return render(request, 'partials/calendar.html', {
            'calendar_weeks': calendar_weeks,
            'lessons_by_day': lessons_by_day,
            'today': today
        })




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


class StartLessonWizardView(LoginRequiredMixin, View):
    def get_section(self, request, section_id):
        return get_object_or_404(Section, id=section_id, tutor=request.user)

    def get_lesson(self, request):
        lesson_id = request.session.get('lesson_id')
        if lesson_id:
            return get_object_or_404(Lesson, id=lesson_id, section__tutor=request.user)
        return None

    def get(self, request, section_id, step):
        section = self.get_section(request, section_id)
        step = int(step)
        lesson = self.get_lesson(request)

        print('get', step)

        # Step 1: basic info
        if step == 1:
            form = LessonStep1Form(instance=lesson)

        # Step 2: optional info
        elif step == 2:
            form = LessonStep2Form(instance=lesson)

        # Step 3+: student edits
        else:
            students = list(section.students.all())
            index = step - 3

            if index >= len(students):
                # Final step: generate plan and redirect
                lesson.lesson_plan = f"Lesson Plan for {lesson.name} on {lesson.topic}."
                lesson.save()
                request.session.pop('lesson_id', None)
                return redirect('section_detail', pk=section.id)

            student = students[index]
            form = StudentForm(instance=student)

        return render(request, f'lessons/start_lesson_step.html', {
            'form': form,
            'step': step,
            'section': section,
        })

    def post(self, request, section_id, step):
        section = self.get_section(request, section_id)
        step = int(step)
        lesson = self.get_lesson(request)

        print('post', step)

        if step == 1:
            form = LessonStep1Form(request.POST, instance=lesson)
            if form.is_valid():
                new_lesson = form.save(commit=False)
                new_lesson.section = section
                new_lesson.save()
                request.session['lesson_id'] = new_lesson.id
                return redirect('start_lesson', section_id=section.id, step=2)

        elif step == 2:
            form = LessonStep2Form(request.POST, instance=lesson)
            if form.is_valid():
                form.save()
                return redirect('start_lesson', section_id=section.id, step=3)

        else:
            students = list(section.students.all())
            index = step - 3
            if index >= len(students):
                return redirect('start_lesson', section_id=section.id, step=step + 1)

            student = students[index]
            form = StudentForm(request.POST, instance=student)
            if form.is_valid():
                form.save()
                return redirect('start_lesson', section_id=section.id, step=step + 1)

        return render(request, f'lessons/start_lesson_step.html', {
            'form': form,
            'step': step,
            'section': section,
        })


class LessonListView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request, section_id):
        section = get_object_or_404(Section, id=section_id, tutor=request.user)
        lessons = section.lessons.all().order_by('date')
        return render(request, 'lessons/lesson_list.html', {
            'section': section,
            'lessons': lessons
        })

    def test_func(self):
        section = get_object_or_404(Section, id=self.kwargs['section_id'])
        return section.tutor == self.request.user


class LessonUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Lesson
    form_class = LessonForm
    template_name = 'lessons/lesson_form.html'

    def get_success_url(self):
        return reverse_lazy('lesson_detail', kwargs={'pk': self.object.id})

    def test_func(self):
        return self.get_object().section.tutor == self.request.user


class GenerateLessonPlanView(LoginRequiredMixin, UserPassesTestMixin, View):
    def post(self, request, pk):
        lesson = get_object_or_404(Lesson, pk=pk)

        if lesson.section.tutor != request.user:
            return self.handle_no_permission()

        lesson.generate_lesson_plan()
        messages.success(request, "Lesson plan regenerated!")

        return redirect('lesson_detail', pk=lesson.id)

    def test_func(self):
        lesson = get_object_or_404(Lesson, pk=self.kwargs['pk'])
        return lesson.section.tutor == self.request.user


class LessonDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Lesson
    template_name = 'lessons/lesson_detail.html'
    context_object_name = 'lesson'

    def test_func(self):
        return self.get_object().section.tutor == self.request.user