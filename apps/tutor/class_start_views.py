from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from .forms import SectionStep1Form, SectionStep2Form, SectionStep3Form, InlineStudentForm
from .models import Section
from django.contrib import messages


class StartSectionWizardView(View):
    def get(self, request, step=1):
        step = int(step)
        if step == 1:
            form = SectionStep1Form()
        elif step == 2:
            form = SectionStep2Form()
        elif step == 3:
            form = SectionStep3Form(user=request.user)
        else:
            return redirect('home')
        if step == 1 or step == 2:
            return render(request, f'sections/start_section_step.html', {'form': form, 'step': step})
        return render(request, f'sections/start_section_step{step}.html', {'form': form, 'step': step})

    def post(self, request, step=1):
        step = int(step)

        # Step 1 → Step 2
        if step == 1:
            form = SectionStep1Form(request.POST)
            if form.is_valid():
                section = form.save(commit=False)
                section.tutor = request.user
                section.save()

                request.session['section_id'] = section.id
                return redirect('start_section', step=2)

        # Step 2 → Step 3
        elif step == 2:
            section = get_object_or_404(Section, pk=request.session.get('section_id'))

            if request.method == 'POST':
                form = SectionStep2Form(request.POST, instance=section)
                if form.is_valid():
                    form.save()
                    return redirect('start_section', step=3)
            else:
                form = SectionStep2Form(instance=section)

            return render(request, 'sections/start_section_step.html', {'form': form, 'step': step})


        # Step 3 → Save + Redirect
        elif step == 3:
            section = get_object_or_404(Section, pk=request.session.get('section_id'))
            section_form = SectionStep3Form(request.POST or None, instance=section, user=request.user)
            student_form = InlineStudentForm(request.POST or None)

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

                    # Generate syllabus
                    section.generate_syllabus()

                    request.session.pop('section_id', None)
                    return redirect('section_detail', pk=section.pk)

            return render(request, 'sections/start_section_step3.html', {
                'form': section_form,
                'student_form': student_form,
                'step': step
            })

        return render(request, f'sections/start_section_step{step}.html', {'form': form, 'step': step})
