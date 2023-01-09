import json
from django.views import generic, View
from django.urls import reverse_lazy
from django.contrib import messages
from django.conf import settings
from django.db.models import Prefetch
from django.http import HttpResponseBadRequest, HttpResponseForbidden, JsonResponse

from .models import Post, Tag, LikeOrDislike
from .forms import PostEditForm, ImageInlineFormset, TagEditForm
from .utils import UserCanEditPostMixin
from auth_with_email.utils import RegistrationCompletedMixin


class PostListView(generic.ListView):
    template_name = "posts/posts_list.html"
    paginate_by = settings.PAGINATE_BY
    model = Post

    @staticmethod
    def prefetch_related(queryset):
        return queryset \
            .select_related("added_by") \
            .prefetch_related("images") \
            .prefetch_related("tags") \
            .prefetch_related(
                Prefetch("reactions", queryset=LikeOrDislike.objects.filter(is_like=True), to_attr="query_likes")) \
            .prefetch_related(
                Prefetch("reactions", queryset=LikeOrDislike.objects.filter(is_dislike=True), to_attr="query_dislikes"))

    def get_queryset(self):
        return self.prefetch_related(Post.objects.all())


class CurrentUserPostsListView(RegistrationCompletedMixin, PostListView):
    template_name = "posts/current_user_posts_list.html"

    def get_queryset(self):
        return self.prefetch_related(Post.objects.filter(added_by=self.request.user))


class PostView(generic.DetailView):
    template_name = "posts/post_view.html"
    model = Post


class PostEditView(RegistrationCompletedMixin, UserCanEditPostMixin, generic.edit.UpdateView):
    model = Post
    form_class = PostEditForm

    message_prefix = "Post update"
    template_name = "posts/post_edit.html"

    def get_form_kwargs(self):
        # add request user to the form for user tags filtering
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_object(self, queryset=None):
        try:
            return super().get_object(queryset)
        except AttributeError:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['image_formset'] = ImageInlineFormset(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['image_formset'] = ImageInlineFormset(instance=self.object)
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form(self.form_class)
        image_formset = ImageInlineFormset(self.request.POST, self.request.FILES, instance=self.object)

        if form.is_valid() and image_formset.is_valid():
            return self.form_valid(form, image_formset)
        else:
            return self.form_invalid(form)

    def form_valid(self, form, image_formset):
        form.instance.added_by = self.request.user
        result = super().form_valid(form)

        # save changed images
        images = image_formset.save(commit=False)
        for image in images:
            image.post = self.object
            image.save()

        # process deleted images
        for image in image_formset.deleted_objects:
            image.delete()

        messages.add_message(self.request, messages.SUCCESS, self.message_prefix + " successfully.")
        return result

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, self.message_prefix + " failed")
        return super().form_invalid(form)


class PostCreateView(PostEditView):
    message_prefix = "Post create"
    template_name = "posts/post_create.html"


class PostDeleteView(RegistrationCompletedMixin, UserCanEditPostMixin, generic.DeleteView):
    model = Post
    template_name = "posts/post_delete.html"
    success_url = reverse_lazy("posts:posts_list")

    def form_valid(self, form):
        messages.add_message(self.request, messages.WARNING, "Post deleted")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "Post delete failed")
        return super().form_invalid(form)


class CurrentUserTagListView(RegistrationCompletedMixin, generic.FormView):
    template_name = "posts/tags_list.html"
    form_class = TagEditForm
    success_url = reverse_lazy("posts:current_user_tags_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = Tag.objects.filter(added_by=self.request.user)
        context["form"].fields["tag"].label = "Add new tag"
        return context

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.form_class)
        if form.is_valid():
            return self.form_valid(form)
        return self.form_invalid(form)

    def form_valid(self, form):
        cleaned_data = form.cleaned_data
        Tag.objects.create(added_by=self.request.user, **cleaned_data)

        return super().form_valid(form)


class LikeDislikeView(RegistrationCompletedMixin, View):
    def get(self, request, *args, **kwargs):
        return HttpResponseForbidden()

    def post(self, request, pk, *args, **kwargs):
        # get Post instance
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return HttpResponseBadRequest()

        # user can't like/dislike his own posts
        if request.user == post.added_by:
            return HttpResponseForbidden()

        try:
            data = json.loads(request.body)
            action = data.get("action", None)
        except json.decoder.JSONDecodeError:
            return HttpResponseBadRequest()

        if action == "like":
            post.toggle_like(request.user)
        elif action == "dislike":
            post.toggle_dislike(request.user)
        else:
            return HttpResponseBadRequest()

        return JsonResponse({"likes": len(post.likes), "dislikes": len(post.dislikes)})

