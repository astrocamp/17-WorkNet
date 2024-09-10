from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from apps.posts.forms.posts_form import PostForm
from apps.posts.models import Post

from lib.models.paginate_queryset import paginate_queryset

from .forms.company_form import CompanyForm
from .models import Company


def index(request):
    if request.method == "POST":
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.user = request.user
            company.save()
            return redirect("companies:index")
    companies = Company.objects.order_by("-id")

    favorited_status = [
        {"company": company, "favorited": company.is_favorited_by(request.user)}
        for company in companies
    ]

    page_obj = paginate_queryset(request, favorited_status, 10)
    return render(request, "companies/index.html", {"page_obj": page_obj})


def new(request):
    form = CompanyForm()
    return render(request, "companies/new.html", {"form": form})


def edit(request, id):
    company = get_object_or_404(Company, id=id)
    form = CompanyForm(instance=company)
    return render(request, "companies/edit.html", {"form": form, "company": company})


def show(request, id):
    if request.method == "POST":
        company = get_object_or_404(Company, id=id)
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return redirect("companies:show", company.id)
        else:
            return render(
                request,
                "companies/edit.html",
                {"form": form, "company": company},
            )

    company = get_object_or_404(Company, id=id)
    return render(request, "companies/show.html", {"company": company})


@require_POST
def delete(request, id):
    company = get_object_or_404(Company, id=id)
    company.mark_delete()
    return redirect("companies:index")


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
    return render(request, "posts/index.html", {"posts": posts, "company": company})


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

        return redirect(reverse("companies:post_index", args=[company.id]))
    else:
        form = PostForm()
    return render(request, "posts/new.html", {"form": form, "company": company})
