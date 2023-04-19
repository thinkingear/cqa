from django.forms import ModelForm
from .models import Course


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['title', 'thumbnail', 'description', 'overview', 'visibility']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['overview'].widget.attrs.update({'class': 'tinymce-editor'})
