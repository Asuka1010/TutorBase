from django import forms
from .models import Student, Section, Lesson


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['tutor']
        widgets = {
            'goals': forms.Textarea(attrs={'rows': 2}),
            'personality': forms.Textarea(attrs={'rows': 2}),
            'interests': forms.Textarea(attrs={'rows': 2}),
            'hobbies': forms.Textarea(attrs={'rows': 2}),
            'current_grades': forms.Textarea(attrs={'rows': 2}),
            'weak_areas': forms.Textarea(attrs={'rows': 2}),
        }


from django.forms import ModelMultipleChoiceField


class SectionForm(forms.ModelForm):
    students = ModelMultipleChoiceField(
        queryset=Student.objects.none(),  # overridden below
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Section
        exclude = ['tutor', 'syllabus', 'learning_objective']
        widgets = {
            'frameworks': forms.Textarea(attrs={'rows': 2}),
            'goals': forms.Textarea(attrs={'rows': 2}),
            'student_characteristics': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['students'].queryset = Student.objects.filter(tutor=user)


class SectionStep1Form(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['name', 'theme', 'number_of_lessons', 'length_of_session']


class SectionStep2Form(forms.ModelForm):
    class Meta:
        model = Section
        fields = ['subject', 'level', 'frameworks', 'goals']


class SectionStep3Form(forms.ModelForm):
    students = forms.ModelMultipleChoiceField(
        queryset=Student.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Section
        fields = ['student_characteristics']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['students'].queryset = Student.objects.filter(tutor=user)


class InlineStudentForm(forms.ModelForm):
    class Meta:
        model = Student
        exclude = ['tutor']
        widgets = {
            'goals': forms.Textarea(attrs={'rows': 2}),
            'personality': forms.Textarea(attrs={'rows': 2}),
            'interests': forms.Textarea(attrs={'rows': 2}),
            'hobbies': forms.Textarea(attrs={'rows': 2}),
            'current_grades': forms.Textarea(attrs={'rows': 2}),
            'weak_areas': forms.Textarea(attrs={'rows': 2}),
        }


class LessonStep1Form(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['date', 'name', 'topic', 'grade_level', 'duration']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


class LessonStep2Form(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['objectives', 'materials', 'other_details']
        widgets = {
            'objectives': forms.Textarea(attrs={'rows': 3}),
            'materials': forms.Textarea(attrs={'rows': 3}),
            'other_details': forms.Textarea(attrs={'rows': 3}),
        }


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['date', 'name', 'topic', 'grade_level', 'duration', 'objectives', 'materials', 'other_details']
        widgets = {
            'date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'objectives': forms.Textarea(attrs={'rows': 3}),
            'materials': forms.Textarea(attrs={'rows': 3}),
            'other_details': forms.Textarea(attrs={'rows': 3}),
        }