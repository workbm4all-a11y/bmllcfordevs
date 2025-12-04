from django.db import models

from student.models import Student
class Course(models.Model):
   course_name = models.CharField(max_length=50000000)
   question_number = models.PositiveIntegerField()
   total_marks = models.PositiveIntegerField()
   def __str__(self):
        return self.course_name

class Question(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    marks=models.PositiveIntegerField()
    question=models.CharField(max_length=6000)
    option1=models.CharField(max_length=2000)
    option2=models.CharField(max_length=2000)
    option3=models.CharField(max_length=2000)
    option4=models.CharField(max_length=2000)
    cat=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    answer=models.CharField(max_length=2000,choices=cat)

class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Course,on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)

# --------------------------
# Auto-fix for Question.answer after Excel upload
# --------------------------
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Question)
def fix_question_answer(sender, instance, created, **kwargs):
    """
    Agar answer Excel se number (1-4) aa gaya hai,
    to automatic Option1/Option2/Option3/Option4 me convert kare.
    """
    # Sirf newly created questions ke liye check karo
    if created and str(instance.answer).isdigit():
        mapping = {'1': 'Option1', '2': 'Option2', '3': 'Option3', '4': 'Option4'}
        instance.answer = mapping[str(instance.answer)]
        # update_fields use kar ke save karo, recursion avoid karne ke liye
        instance.save(update_fields=['answer'])
