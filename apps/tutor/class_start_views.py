from .forms import (
    SectionStep1Form, SectionStep2Form, SectionStep3Form,
    InlineStudentForm, SectionResourceFormSet
)
from .models import Section
from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin


class StartSectionWizardView(LoginRequiredMixin, View):
    def get(self, request, step=1):
        step = int(step)
        if step == 1:
            form = SectionStep1Form()
            return render(request, 'sections/start_section_step.html', {'form': form, 'step': step})

        section = get_object_or_404(Section, pk=request.session.get('section_id'))

        if step == 2:
            form = SectionStep2Form(instance=section)
            resource_formset = SectionResourceFormSet(instance=section)
            return render(request, 'sections/start_section_step2.html', {
                'form': form,
                'resource_formset': resource_formset,
                'step': step
            })

        elif step == 3:
            section_form = SectionStep3Form(instance=section, user=request.user)
            student_form = InlineStudentForm()
            return render(request, 'sections/start_section_step3.html', {
                'form': section_form,
                'student_form': student_form,
                'step': step
            })

        return redirect('home')

    def post(self, request, step=1):
        step = int(step)

        if step == 1:
            form = SectionStep1Form(request.POST)
            if form.is_valid():
                section = form.save(commit=False)
                section.tutor = request.user
                section.save()
                request.session['section_id'] = section.id
                return redirect('start_section', step=2)
            return render(request, 'sections/start_section_step.html', {'form': form, 'step': step})

        section = get_object_or_404(Section, pk=request.session.get('section_id'))

        if step == 2:
            form = SectionStep2Form(request.POST, instance=section)
            resource_formset = SectionResourceFormSet(request.POST, request.FILES, instance=section)

            if form.is_valid() and resource_formset.is_valid():
                form.save()
                resource_formset.save()
                return redirect('start_section', step=3)

            return render(request, 'sections/start_section_step.html', {
                'form': form,
                'resource_formset': resource_formset,
                'step': step
            })

        elif step == 3:
            section_form = SectionStep3Form(request.POST, instance=section, user=request.user)
            student_form = InlineStudentForm(request.POST)

            if 'add_student' in request.POST:
                if student_form.is_valid():
                    new_student = student_form.save(commit=False)
                    new_student.tutor = request.user
                    new_student.save()
                    messages.success(request, f"Student '{new_student.name}' added.")
                    return redirect('start_section', step=3)

            elif 'submit_section' in request.POST:
                if section_form.is_valid():
                    section = section_form.save()
                    section.students.set(section_form.cleaned_data['students'])
                    section.generate_syllabus()
                    request.session.pop('section_id', None)
                    return redirect('section_detail', pk=section.pk)

            return render(request, 'sections/start_section_step3.html', {
                'form': section_form,
                'student_form': student_form,
                'step': step
            })

        return redirect('home')
