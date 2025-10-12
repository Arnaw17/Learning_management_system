from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.student_login, name='student_login'),
    path('logout/', views.logout_view, name='logout_view'),
    path('register/', views.student_register, name='student_register'),

    # Instructor
    path('instructor/login/', views.instructor_login, name='instructor_login'),
    path('instructor/register/', views.instructor_register, name='instructor_register'),
    path('instructor/dashboard/', views.instructor_dashboard, name='instructor_dashboard'),
    path('instructor/create-course/', views.instructor_create_course, name='instructor_create_course'),
    path('instructor/manage-courses/', views.instructor_manage_courses, name='instructor_manage_courses'),
    path('instructor/add-quiz/', views.instructor_add_quiz, name='instructor_add_quiz'),
    path('instructor/create-coupon/', views.instructor_create_coupon, name='instructor_create_coupon'),
    path('instructor/engagement/', views.instructor_engagement, name='instructor_engagement'),
    path('instructor/request-payout/', views.instructor_request_payout, name='instructor_request_payout'),

    # Courses
    path('courses/python/', views.course_python, name='course_python'),
    path('courses/javascript/', views.course_javascript, name='course_javascript'),
    path('courses/java/', views.course_java, name='course_java'),
    path('courses/cpp/', views.course_cpp, name='course_cpp'),
    path('purchase/', views.purchase_course, name='purchase_course'),
]
