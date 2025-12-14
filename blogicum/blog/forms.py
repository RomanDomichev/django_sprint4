
from django import forms
from .models import Post, Category, Location, Comment

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text', 'pub_date', 'location', 'category', 'image')
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'text': forms.Textarea(attrs={'rows': 5}),
        }
        help_texts = {
            'pub_date': 'Если установить дату и время в будущем — можно делать отложенные публикации.',
            'is_published': 'Снимите галочку, чтобы скрыть публикацию.',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.filter(is_published=True)
        self.fields['location'].queryset = Location.objects.filter(is_published=True)

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'text': 'Текст комментария',
        }