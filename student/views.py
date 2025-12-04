from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from quiz import models as QMODEL
from teacher import models as TMODEL


# ------------------------------------------------
# Student Authentication
# ------------------------------------------------

def studentclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'student/studentclick.html')


def student_signup_view(request):
    userForm = forms.StudentUserForm()
    studentForm = forms.StudentForm()
    mydict = {'userForm': userForm, 'studentForm': studentForm}

    if request.method == 'POST':
        userForm = forms.StudentUserForm(request.POST)
        studentForm = forms.StudentForm(request.POST, request.FILES)
        if userForm.is_valid() and studentForm.is_valid():
            user = userForm.save()
            user.set_password(user.password)
            user.save()

            student = studentForm.save(commit=False)
            student.user = user
            student.save()

            my_student_group = Group.objects.get_or_create(name='STUDENT')
            my_student_group[0].user_set.add(user)

        return HttpResponseRedirect('studentlogin')

    return render(request, 'student/studentsignup.html', context=mydict)


def is_student(user):
    return user.groups.filter(name='STUDENT').exists()


# ------------------------------------------------
# Dashboard
# ------------------------------------------------

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_dashboard_view(request):
    context = {
        'total_course': QMODEL.Course.objects.all().count(),
        'total_question': QMODEL.Question.objects.all().count(),
    }
    return render(request, 'student/student_dashboard.html', context)


# ------------------------------------------------
# Exams
# ------------------------------------------------

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_exam_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request, 'student/student_exam.html', {'courses': courses})


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def take_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    questions = QMODEL.Question.objects.filter(course=course).order_by('id')

    total_questions = questions.count()
    total_marks = sum(q.marks for q in questions)

    context = {
        'course': course,
        'total_questions': total_questions,
        'total_marks': total_marks,
    }
    return render(request, 'student/take_exam.html', context)


@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def start_exam_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    questions = QMODEL.Question.objects.filter(course=course).order_by('id')

    if request.method == 'POST':
        pass

    response = render(request, 'student/start_exam.html', {
        'course': course,
        'questions': questions
    })
    response.set_cookie('course_id', course.id)
    return response


# ------------------------------------------------
# Result Calculation — FIXED
# ------------------------------------------------

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def calculate_marks_view(request):
    if request.COOKIES.get('course_id') is None:
        return redirect('student-marks')

    course_id = request.COOKIES.get('course_id')
    course = QMODEL.Course.objects.get(id=course_id)

    total_marks = 0
    questions = QMODEL.Question.objects.filter(course=course).order_by('id')

    # Fixed: correct answer comparison
    for i, q in enumerate(questions, start=1):
        selected_ans = request.COOKIES.get(str(i))  # always string
        actual_answer = str(q.answer).strip()       # Excel answer (string)

        if selected_ans and selected_ans.strip() == actual_answer:
            total_marks += q.marks

    # Save result
    student = models.Student.objects.get(user_id=request.user.id)
    QMODEL.Result.objects.create(
        marks=total_marks,
        exam=course,
        student=student
    )

    # Cleanup cookies
    response = redirect('check-marks', pk=course.id)
    response.delete_cookie('course_id')

    for i in range(1, len(questions) + 1):
        response.delete_cookie(str(i))

    return response


# ------------------------------------------------
# View Result
# ------------------------------------------------

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def view_result_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request, 'student/view_result.html', {'courses': courses})


# ------------------------------------------------
# Check Marks — Single Exam Result
# ------------------------------------------------

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def check_marks_view(request, pk):
    course = QMODEL.Course.objects.get(id=pk)
    student = models.Student.objects.get(user_id=request.user.id)

    results = QMODEL.Result.objects.filter(exam=course, student=student)

    if results.exists():
        result = results.last()
        obtained_marks = result.marks
        total_questions = QMODEL.Question.objects.filter(course=course).count()
        total_marks = sum(q.marks for q in QMODEL.Question.objects.filter(course=course))
        percentage = round((obtained_marks / total_marks) * 100, 2)
    else:
        obtained_marks = 0
        total_marks = 0
        total_questions = 0
        percentage = 0

    context = {
        'results': results,
        'course': course,
        'obtained_marks': obtained_marks,
        'total_marks': total_marks,
        'total_questions': total_questions,
        'percentage': percentage,
    }
    return render(request, 'student/check_marks.html', context)


# ------------------------------------------------
# Marks List
# ------------------------------------------------

@login_required(login_url='studentlogin')
@user_passes_test(is_student)
def student_marks_view(request):
    courses = QMODEL.Course.objects.all()
    return render(request, 'student/student_marks.html', {'courses': courses})
