import json

import rules
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST

from apps.jobs.forms import JobForm
from apps.jobs.models import Job, Job_Resume, JobFavorite
from apps.posts.forms.posts_form import PostForm
from apps.posts.models import Post
from lib.models.paginate import paginate_queryset
from lib.models.rule_required import rule_required
from lib.utils.models.decorators import company_required

from .forms.companies_form import CompanyForm
from .models import Company
from apps.resumes.models import Resume
from apps.users.models import UserInfo
from lib.utils.models.defined import LOCATION_CHOICES


def index(request):
    if request.method == "POST":
        company = get_object_or_404(Company, user=request.user)
        form = CompanyForm(request.POST, instance=company)

        if form.is_valid():
            form.save()

            messages.success(request, "新增成功")
            return redirect("companies:index")
    companies = Company.objects.order_by("-id")

    company_data = [
        {
            "company": company,
            "favorited": company.is_favorited_by(request.user),
            "can_edit": rules.test_rule("can_edit_company", request.user, company.id),
        }
        for company in companies
    ]

    page_obj = paginate_queryset(request, company_data, 10)
    return render(request, "companies/index.html", {"page_obj": page_obj})


@rule_required("can_new_company")
def new(request):
    company, _ = Company.objects.get_or_create(
        user_id=request.user.id,
        defaults={
            "employees": 0,
        },
    )
    form = CompanyForm(instance=company)
    return render(request, "companies/new.html", {"form": form})


@rule_required("can_edit_company")
def edit(request, id):
    company = get_object_or_404(Company, id=id)
    form = CompanyForm(instance=company)
    return render(request, "companies/edit.html", {"form": form, "company": company})


def show(request, id):
    company = get_object_or_404(Company, id=id)
    if request.method == "POST":
        company = get_object_or_404(Company, id=id)
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, "更新成功")
            return redirect("companies:show", company.id)
        else:
            return render(
                request,
                "companies/edit.html",
                {"form": form, "company": company},
            )

    posts = Post.objects.filter(company=company).order_by("-created_at")[:10]
    posts_data = [
        {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "score": post.score,
            "created_at": post.created_at,
            "user": post.user,
            "can_edit": (
                rules.test_rule("can_edit_post", request.user, post)
                if request.user.is_authenticated
                else False
            ),
        }
        for post in posts
    ]

    user_resume = []
    if request.user.is_authenticated and 1 == request.user.type:
        user_info = UserInfo.objects.get(user=request.user)
        user_resume = Resume.objects.filter(userinfo=user_info).values_list(
            "id", flat=True
        )
    location_dict = dict(LOCATION_CHOICES)
    jobs = Job.objects.filter(company=company).order_by("-created_at")[:5]
    jobs_data = [
        {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "type": job.type,
            "location_label": location_dict.get(job.location),
            "location": job.location,
            "salary": job.salary_range,
            "created_at": job.created_at,
            "favorited": (
                JobFavorite.objects.filter(job=job, user=request.user).exists()
                if request.user.is_authenticated
                else False
            ),
            "apply": Job_Resume.objects.filter(
                job=job, resume__in=user_resume
            ).exists(),
        }
        for job in jobs
    ]

    return render(
        request,
        "companies/show.html",
        {"company": company, "jobs": jobs_data, "posts": posts_data},
    )


@login_required
def favorite(request, id):
    company = get_object_or_404(Company, pk=id)
    if request.method == "POST":
        company.mark_delete()
        return redirect("companies:index")


@require_POST
def favorite_company(request, id):
    company = get_object_or_404(Company, pk=id)
    user = request.user
    favorited = company.is_favorited_by(user)

    if favorited:
        company.favorite.remove(user)
    else:
        company.favorite.add(user)

    return render(
        request,
        "companies/favorite.html",
        {"company": company, "favorited": not favorited},
    )


def post_index(request, id):
    company = get_object_or_404(Company, id=id)
    posts = Post.objects.filter(company=company).order_by("-created_at")

    posts_with_permissions = [
        {"post": post, "can_edit": rules.test_rule("can_edit_post", request.user, post)}
        for post in posts
    ]
    page_obj = paginate_queryset(request, posts_with_permissions, 10)

    return render(
        request, "posts/index.html", {"page_obj": page_obj, "company": company}
    )


@login_required
@require_http_methods(["GET", "POST"])
def post_new(request, id):
    company = get_object_or_404(Company, id=id)
    form = PostForm(request.POST)
    if form.is_valid():
        post = form.save(commit=False)
        post.company = company
        post.user = request.user
        post.save()

        messages.success(request, "新增成功")
        return redirect(reverse("posts:show", args=[post.id]))
    else:
        form = PostForm()
    return render(request, "posts/new.html", {"form": form, "company": company})


def jobs_index(request, id):
    company = get_object_or_404(Company, id=id)
    jobs = (
        Job.objects.filter(company=company)
        .order_by("-created_at")
        .select_related("company")
    )
    jobs_with_permissions = [
        {"job": job, "can_edit": True, "company": job.company} for job in jobs
    ]
    page_obj = paginate_queryset(request, jobs_with_permissions, 10)

    return render(
        request, "jobs/index.html", {"page_obj": page_obj, "company": company}
    )


@login_required
def jobs_new(request, id):
    company = get_object_or_404(Company, id=id)
    form = JobForm(request.POST)
    if form.is_valid():
        job = form.save(commit=False)
        job.company = company
        job.save()

        tags = request.POST.get("tags")
        if tags:
            tags = [tag["value"] for tag in json.loads(tags)]
            job.tags.add(*tags)
            job.save()
        messages.success(request, "新增成功")
        return redirect(reverse("companies:jobs_index", args=[company.id]))
    else:
        form = JobForm()
    return render(request, "jobs/new.html", {"form": form, "company": company})


@company_required
def company_application(request):
    company = request.user.company
    applications = Job_Resume.objects.filter(job__company=company).order_by(
        "-created_at"
    )

    return render(
        request, "companies/applications.html", {"applications": applications}
    )
