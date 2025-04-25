from django.db import models
from django.contrib.auth.models import User


class Student(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=300)
    language = models.CharField(max_length=300, null=True, blank=True)
    country = models.CharField(max_length=300, verbose_name="Country of Residence", null=True, blank=True)
    goals = models.TextField(null=True, blank=True)
    personality = models.TextField(null=True, blank=True)
    interests = models.TextField(null=True, blank=True)
    hobbies = models.TextField(null=True, blank=True)
    current_grades = models.TextField(null=True, blank=True)

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
        self.save()

    def student_names(self):
        return ", ".join(student.name for student in self.students.all())

