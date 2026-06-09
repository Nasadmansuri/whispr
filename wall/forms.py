from django import forms
from .models import Confession, Board

MAX_IMAGE_SIZE_MB = 5
MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024
MAX_VIDEO_SIZE_MB = 10
MAX_VIDEO_SIZE_BYTES = MAX_VIDEO_SIZE_MB * 1024 * 1024
ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
ALLOWED_VIDEO_TYPES = ['video/mp4', 'video/webm', 'video/ogg', 'video/quicktime']

class ConfessionForm(forms.ModelForm):
    class Meta:
        model = Confession
        fields = ['message', 'board', 'is_anonymous', 'mood', 'image', 'video']
        widgets = {
            'message': forms.Textarea(attrs={'placeholder': 'Yo cheez chai koi lai nabhanau...', 'rows': 4}),
            'is_anonymous': forms.CheckboxInput(),
            'image': forms.FileInput(),
            'video': forms.FileInput(),
            'board': forms.Select(),
        }
        labels = {
            'message': 'Confession',
            'is_anonymous': 'Post Anonymously?',
            'mood': 'Mood',
            'image': 'Attach an Image (optional)',
            'video': 'Attach a Video (optional)',
            'board': 'Post to Board (optional)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['board'].queryset = Board.objects.all()
        self.fields['board'].empty_label = '🌐 General Wall (no board)'
        self.fields['board'].required = False

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if image.size > MAX_IMAGE_SIZE_BYTES:
                raise forms.ValidationError(f'Image too large. Max size is {MAX_IMAGE_SIZE_MB}MB.')
            if image.content_type not in ALLOWED_IMAGE_TYPES:
                raise forms.ValidationError('Invalid file type. Use JPG, PNG, GIF, or WebP.')
        return image

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            if video.size > MAX_VIDEO_SIZE_BYTES:
                raise forms.ValidationError(f'Video too large. Max size is {MAX_VIDEO_SIZE_MB}MB.')
            if video.content_type not in ALLOWED_VIDEO_TYPES:
                raise forms.ValidationError('Invalid video type. Use MP4, WebM, OGG, or MOV.')
        return video

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get('image')
        video = cleaned_data.get('video')
        if image and video:
            raise forms.ValidationError('Please attach either an image or a video, not both.')
        return cleaned_data


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g. college, relationships, work'}),
            'description': forms.Textarea(attrs={'placeholder': 'What is this board about?', 'rows': 3}),
        }
        labels = {
            'name': 'Board Name',
            'description': 'Description',
        }
