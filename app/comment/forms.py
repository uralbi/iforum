from django import forms
from django.contrib.contenttypes.models import ContentType
from core.models import Comment
from crispy_forms.layout import Submit
from crispy_forms.helper import FormHelper


class CommentForm(forms.ModelForm):
     content = forms.CharField(widget=forms.Textarea(attrs={'rows': 2}))

     class Meta:
        model = Comment
        fields = ['content']

     def __init__(self, *args, **kwargs):
          super(CommentForm, self).__init__(*args, **kwargs)
          self.helper = FormHelper()
          self.fields['content'].label = ''
          self.helper.add_input(Submit('submit', 'Comment'))
