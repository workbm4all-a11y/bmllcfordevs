from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from .models import Course, Question, Result

@admin.register(Course)
class CourseAdmin(ImportExportModelAdmin):
    list_display = ('course_name', 'question_number', 'total_marks')

@admin.register(Question)
class QuestionAdmin(ImportExportModelAdmin):
    list_display = ('question', 'course', 'marks', 'answer')

@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'marks')
from quiz.models import Question

# Loop through all questions and fix the answer field
for q in Question.objects.all():
    if q.answer.isdigit():  # agar answer Excel se number aa gaya
        mapping = {'1': 'Option1', '2': 'Option2', '3': 'Option3', '4': 'Option4'}
        q.answer = mapping[q.answer]
        q.save()

print("✅ All answers fixed successfully!")
