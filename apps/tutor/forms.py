from django import forms
from .models import Student, Section, Lesson, Resource
from django.forms import ModelMultipleChoiceField
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Field


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


class ResourceForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ['name', 'url', 'file']
        widgets = {
            'url': forms.URLInput(attrs={'placeholder': 'https://...'}),
            'file': forms.ClearableFileInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False  # Don't wrap each subform in <form>
        self.helper.layout = Layout(
            Row(
                Column(Field('name'), css_class='col-md-4'),
                Column(Field('url'), css_class='col-md-4'),
                Column(Field('file'), css_class='col-md-4'),
            ),
            Row(
                Column('DELETE', css_class='col-md-2') if 'DELETE' in self.fields else ''
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        url = cleaned_data.get('url')
        file = cleaned_data.get('file')

        if name:
            if bool(url) == bool(file):  # both provided or neither
                raise forms.ValidationError("Provide either a URL or a file (not both) when a name is entered.")


SectionResourceFormSet = inlineformset_factory(
    Section, Resource,
    form=ResourceForm,
    extra=1,
    can_delete=True
)

LessonResourceFormSet = inlineformset_factory(
    Lesson, Resource,
    form=ResourceForm,
    extra=1,
    can_delete=True
)