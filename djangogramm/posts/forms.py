from django import forms

from .models import Post, Image, Tag


class PostEditForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)

        super().__init__(*args, **kwargs)
        self.fields["tags"].required = False

        # Get the post owner from the request (see get_form_kwargs in post create/update view)
        post_owner = self.user

        self.fields["tags"].queryset = Tag.objects.filter(added_by=post_owner)

    class Meta:
        model = Post
        fields = ["title", "text", "tags"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "text": forms.Textarea(attrs={"class": "form-control"}),
            "tags": forms.CheckboxSelectMultiple(attrs={"class": "tag-brown"}),
        }


class ImageEditForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ["image"]
        widgets = {
            "image": forms.FileInput(attrs={"class": "form-control"})
        }


class TagEditForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ["tag"]
        widgets = {
            "tag": forms.TextInput(attrs={"class": "form-control"})
        }


ImageInlineFormset = forms.inlineformset_factory(
    Post,
    Image,
    ImageEditForm,
    extra=1
)
