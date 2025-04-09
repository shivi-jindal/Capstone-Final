from django import forms

from write_on_cue.models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model= Profile
        fields = ('bio', 'picture')

        widgets = {
            'bio': forms.Textarea(attrs = {'id': 'id_bio_input_text', 'rows':'3'}),
            'picture': forms.FileInput(attrs = {'id': 'id_profile_picture'}),
        }
        labels = {
            'bio': "",
            'picture': "Upload image",
        }