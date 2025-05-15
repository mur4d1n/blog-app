from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView
from django.views.generic.edit import FormMixin

from .forms import EmailPostForm
from .models import Post


class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post/detail.html'

    def get_object(self, queryset=None):
        year = self.kwargs['year']
        month = self.kwargs['month']
        day = self.kwargs['day']
        slug = self.kwargs['post']

        return get_object_or_404(
            Post,
            status=Post.Status.PUBLISHED,
            slug=slug,
            publish__year=year,
            publish__month=month,
            publish__day=day,
        )


class PostShareView(FormMixin, DetailView):
    form_class = EmailPostForm
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post/share.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return self.request.path

    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()

        if form.is_valid():
            return self.form_valid(form)

        return self.form_invalid(form)

    def form_valid(self, form):
        cd = form.cleaned_data

        post_url = self.request.build_absolute_uri(self.object.get_absolute_url())
        subject = f"{cd['name']} recommends you read {self.object.title}"
        message = f"Read {self.object.title} at {post_url}\n\n{cd['name']}\'s ({cd['email']}) comments: {cd['comments']}"

        send_mail(subject, message, settings.EMAIL_HOST_USER, [cd['to']])

        return render(self.request, 'blog/post/share.html', {'post': self.object, 'form': form, 'sent': True})
