from rest_framework.views import APIView
from django.shortcuts import render, redirect
from django.core.paginator import Paginator
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.hashers import check_password
from datetime import datetime
from django.db import connection
from .validations import (
    validate_credentials,
)  # for validating the credentials of the user (custom)
from django.http import Http404
from rest_framework.response import Response
from rest_framework import status

# Create your views here.


# def display(request):
#     return render(request, "dashboard.html")


User = get_user_model()  # get the user model that is active in the project


class DashboardViewAPIView(APIView):
    def get(self, request):
        authenticated = request.user.is_authenticated
        user = request.user.first_name if authenticated else None
        return render(
            request, "dashboard.html", {"active_user": authenticated, "user": user}
        )


class RegisterViewAPIView(APIView):
    def post(self, request):
        email = request.POST["email"]
        password = request.POST["password"]
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        gender = request.POST["gender"]
        phone = request.POST["phone"]
        dob = datetime.strptime(request.POST["dob"], "%Y-%m-%d").date()
        address = request.POST["address"]

        validated, message = validate_credentials(
            email=email, password=password, dob=dob, check_email=True
        )

        if not validated:
            return render(
                request,
                "user/register.html",
                context={
                    "error": message,
                    "active_user": request.user.is_authenticated,
                },
            )
        user = User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            dob=dob,
            gender=gender,
        )
        user.save()
        return redirect("/user/login/")

    def get(self, request):
        is_authenticated = request.user.is_authenticated
        return render(
            request, "user/register.html", context={"active_user": is_authenticated}
        )


class LoginViewAPIView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            return redirect("/")
        return render(request, "user/login.html")

    def post(self, request):
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = User.objects.filter(email=email).first()
        if user and check_password(password, user.password):
            login(request, user)
            return redirect("/")
        return render(
            request, "user/login.html", {"error": "Invalid email or password!"}
        )


def LogoutView(request):
    logout(request)
    return redirect("/")


class ViewUsersAPIView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT first_name, last_name, id, email from user_User order by created_at asc"
            )
            users = cursor.fetchall()
        paginator = Paginator(users, 5)
        try:
            page_number = int(request.GET.get("page"))
        except Exception as e:
            page_number = 1

        # page_number = (
        #     int(request.GET.get("page", "1"))
        #     if str(request.GET.get("page", "1")).isdigit()
        #     else 1
        # )

        page_obj = paginator.get_page(page_number)
        user_info = [(user[0].title(), user[1].title(), user[2], user[3]) for user in users]
        user_info = user_info[(page_number - 1) * 5 : 5 * page_number]
        return render(
            request,
            "user/users.html",
            {
                "active_user": request.user.is_authenticated,
                "active_email": request.user.email,
                "users": user_info,
                "page_obj": page_obj,
            },
        )


class UpdateUserAPIView(APIView):
    def get(self, request, pk=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT first_name,last_name,gender,email,phone,dob,address FROM user_User where id={pk}"
            )
            user =cursor.fetchone()
        if user:
            (
                first_name,
                last_name,
                gender,
                email,
                phone,
                dob,
                address,
            ) = user
            context = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "address": address,
                "dob": dob.strftime("%Y-%m-%d"),
                "gender": gender,
                "modify": True,
                "active_user": request.user.is_authenticated,
            }
            return render(request, "user/register.html", context)

    def post(self, request, pk=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        user = User.objects.get(id=pk)
        password = request.POST.get("password")
        email = request.POST.get("email")
        dob = datetime.strptime(request.POST.get("dob"), "%Y-%m-%d").date()

        validated, message = validate_credentials(
            email=email, password=password, dob=dob, check_email=False
        )
        if not validated:
            return render(request, "user/register.html", context={"error": message})
        else: # check if the email is already registered
            usr = User.objects.filter(email=email).exclude(id=pk).first()
            if usr:
                return render(
                    request,
                    "user/register.html",
                    context={"error": "Email address already registered!"},
                )

        user.email = email
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
        if password:
            user.set_password(password)
        user.phone = request.POST.get("phone")
        user.address = request.POST.get("address")
        user.dob = dob
        user.gender = request.POST.get("gender")
        user.updated_at = datetime.now()
        user.save()
        return redirect("/all/")


class DeleteUserAPIView(APIView):
    def get(self, request, pk=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")
        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM user_User WHERE id={pk}")
        return redirect("/all/")


class ViewUserAPIView(APIView):
    def get(self, request, pk=None):
        if not request.user.is_authenticated:
            return redirect("/user/login/")

        with connection.cursor() as cursor:
            cursor.execute(
                f"SELECT first_name,last_name,gender,email,phone,dob,address,created_at,updated_at FROM user_User where id={pk}"
            )
            user = cursor.fetchone()
        if user:
            (
                first_name,
                last_name,
                gender,
                email,
                phone,
                dob,
                address,
                created_at,
                updated_at,
            ) = user
            context = {
                "first_name": first_name.title(),
                "last_name": last_name.title(),
                "email": email,
                "phone": phone,
                "address": address,
                "dob": dob.strftime("%Y-%m-%d"),
                "gender": gender,
                "updated_at": updated_at.strftime("%Y-%m-%d"),
                "created_at": created_at.strftime("%Y-%m-%d"),
                "active_user": request.user.is_authenticated,
            }
            return render(request, "user/user.html", context=context)
