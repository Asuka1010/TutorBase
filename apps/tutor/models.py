from django.db import models
from django.contrib.auth.models import User
from utils.syllabus import SyllabusHelper
from utils.lesson_plan import LessonPlanHelper


class Student(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    language = models.CharField(max_length=300, null=True, blank=True)
    country = models.CharField(max_length=300, verbose_name="Country of Residence", null=True, blank=True)
    goals = models.TextField(null=True, blank=True, verbose_name="Goal & Expectations for Tutors")
    personality = models.TextField(null=True, blank=True)
    interests = models.TextField(null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)
    current_grades = models.TextField(null=True, blank=True, verbose_name="Current Grade Level")
    weak_areas = models.TextField(null=True, blank=True, verbose_name="Identified Weak Areas")

    def __str__(self):
        return self.name


class Section(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=1000, verbose_name="Course Name")
    students = models.ManyToManyField(Student)
    theme = models.CharField(max_length=1000, verbose_name="Course Topic")

    learning_objective = models.TextField(null=True, blank=True)
    subject = models.CharField(max_length=2000,
                               verbose_name="What subject/discipline is this course in?",
                               null=True, blank=True)
    level = models.CharField(max_length=2000,
                             verbose_name="What is the academic level (e.g., K-12 grade level, undergraduate, graduate)?",
                             null=True, blank=True)
    frameworks = models.TextField(verbose_name="Are there any specific standards or frameworks you need to align with (e.g., Common Core, state standards, professional competencies)?",
                                  null=True, blank=True)
    goals = models.TextField(verbose_name="What are the main course goals or key concepts you want students to master?",
                             null=True, blank=True)
    student_characteristics = models.TextField(help_text="Beyond what was entered in each student's profile.", null=True, blank=True)
    number_of_lessons = models.IntegerField()
    length_of_session = models.IntegerField(help_text="in minutes")
    syllabus = models.TextField(null=True, blank=True)

    resources = models.ManyToManyField('Resource', blank=True)

    class Meta:
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self):
        return self.name

    def generate_syllabus(self):
        self.syllabus = f"""📘 Syllabus for {self.name}
        ✨ Theme: {self.theme}
        🎯 Objective: {self.learning_objective}
        📚 Lessons: {self.number_of_lessons}
        ⏱️ Session Length: {self.length_of_session} minutes"""
        syllabus_helper = SyllabusHelper()
        self.syllabus = syllabus_helper.generate(self)
        self.save()

    def student_names(self):
        return ", ".join(student.name for student in self.students.all())


class Lesson(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE, related_name="lessons")
    date = models.DateTimeField()
    name = models.CharField(max_length=500, verbose_name="Name of the Lesson")
    topic = models.CharField(max_length=1000, verbose_name="Topic of Lesson")
    grade_level = models.CharField(max_length=300)
    duration = models.IntegerField(help_text="in minutes", verbose_name="Lesson Duration")

    objectives = models.TextField(blank=True, null=True, verbose_name="What are the objectives for this lesson?")
    materials = models.TextField(blank=True, null=True, verbose_name="What materials (if any) do you want to use?")
    other_details = models.TextField(blank=True, null=True, verbose_name="Any other details about the lesson?")

    resources = models.ManyToManyField('Resource', blank=True)

    lesson_plan = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.date.date()})"

    def generate_lesson_plan(self):
        section = self.section
        syllabus_content = section.syllabus

        lessons = list(section.lessons.order_by('date'))
        session_number = lessons.index(self) + 1 if self in lessons else 1

        self.lesson_plan = f"""📘 Lesson Plan for {self.name}
        📅 Date: {self.date.strftime('%B %d, %Y at %I:%M %p')}
        🎓 Topic: {self.topic}
        🎯 Grade Level: {self.grade_level}
        ⏱️ Duration: {self.duration} minutes
        """
        lesson_plan_helper = LessonPlanHelper()
        self.lesson_plan = lesson_plan_helper.generate(section, session_number, syllabus_content)
        self.save()


class Resource(models.Model):
    name = models.CharField(max_length=1000)
    url = models.URLField(null=True, blank=True)
    file = models.FileField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
