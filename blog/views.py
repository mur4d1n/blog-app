from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView, DetailView

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


def post_share(request, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED,
    )

    sent = False

    if request.method == 'POST':
        form = EmailPostForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n{cd['name']}\'s ({cd['email']}) comments: {cd['comments']}"

            send_mail(subject, message, settings.EMAIL_HOST_USER, [cd['to']])

            sent = True
    else:
        form = EmailPostForm()

    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})
