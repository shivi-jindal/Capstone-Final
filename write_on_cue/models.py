from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.
class Profile(models.Model):
    bio = models.CharField(max_length=200)
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    picture = models.FileField(blank=True)
    content_type = models.CharField(blank=True, max_length=50)
    #cart_items = models.ManyToManyField(Product, related_name = "cart_items")
    #my_items = models.ManyToManyField(Product, related_name = "my_items")
    #liked_products = models.ManyToManyField(Product, related_name='liked_by', blank=True)


    def __str__(self):
        return f'Profile for {self.user.username}'

class AudioRecording(models.Model):
    audio_file = models.FileField(upload_to="audio/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

class Transcription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    audio_file = models.FileField(upload_to='transcriptions/audio/')
    midi_file = models.FileField(upload_to='transcriptions/midi/')
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.JSONField(blank=True, null=True)  # Stores detected notes
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Transcription {self.id} by {self.user.username}"

class SheetMusic(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    original_audio = models.FileField(upload_to='audio/')
    midi_file = models.FileField(upload_to='midi/', null=True, blank=True)
    #musicxml = models.FileField(upload_to='musicxml/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Transcription {self.id} by {self.user.username}"
    
    def get_absolute_url(self):
        return f'/sheet/{self.id}/'