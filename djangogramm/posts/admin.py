from django.contrib import admin
from .models import Post, Tag, Image


class ImageInline(admin.StackedInline):
    model = Image
    fields = ("image", "image_preview")
    readonly_fields = ("image_preview",)
    extra = 0


class PostAdmin(admin.ModelAdmin):
    fields = ("title", "text", "tags")
    list_display = ("title", "added_by", "posted")
    list_display_links = ("title", "added_by", "posted")
    search_fields = ("title", "text", "added_by__username")

    filter_horizontal = ("tags",)

    save_as = True

    inlines = [ImageInline]

    def get_form(self, request, obj=None, change=False, **kwargs):
        # post can be without tags
        form = super().get_form(request, obj=None, change=False, **kwargs)
        form.base_fields['tags'].required = False
        return form

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # filter available tags by post owner
        if db_field.name == "tags":
            # get Post instance
            try:
                post = Post.objects.get(pk=request.resolver_match.kwargs["object_id"])
                user = post.added_by
            except (Post.DoesNotExist, KeyError):
                user = request.user

            kwargs["queryset"] = Tag.objects.filter(added_by=user)

        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        # admin can't add posts by another username.
        if not obj.added_by_id:
            obj.added_by_id = request.user.pk

        super().save_model(request, obj, form, change)


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
