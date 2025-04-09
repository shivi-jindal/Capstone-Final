from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils import timezone

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from write_on_cue.forms import ProfileForm
from write_on_cue.models import Profile, AudioRecording, SheetMusic

from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import subprocess
import os
import tempfile
import io
from music21 import converter
import json
import logging
logger = logging.getLogger(__name__)
import requests
from django.views.decorators.csrf import csrf_exempt

from pprint import pprint
import os
from urllib.request import urlopen
from urllib.error import HTTPError

import flat_api
from flat_api.rest import ApiException
from music21 import converter


#from django.http import HttpResponse, Http404

#from django.core import serializers
#from django.http import HttpResponse, JsonResponse
#from django.conf import settings

#from django.db.models import  Q, Avg

#from transformers import pipeline
#from PIL import Image

# Create your views here.
FLAT_ACCESS_TOKEN = "fb6cb03b077966bae3d08f69eef80248aec606be76f14745301e4e62e1bf0ae8544b500649af9a4067d6afc57f72c4f6b19c204cfea1a213e11865c0b7ba2644"
#MIDI_FILE_PATH = "/Users/user/Documents/capstone/midi_files/melody_anonymous_1743275446.mid"

def convert_midi(MIDI_FILE_PATH):
    print("convert midi called")
    print(MIDI_FILE_PATH)
    configuration = flat_api.Configuration()
    configuration.access_token = os.environ['FLAT_ACCESS_TOKEN']
    flat_api_client = flat_api.ApiClient(configuration)

    try:
        # Convert MIDI to MusicXML and read the content as a string
        try:
            midi = converter.parse(MIDI_FILE_PATH)
        except Exception as e:
            print(f"Error parsing MIDI file: {str(e)}")
            return JsonResponse({'status': 'error', 'message': f'MIDI parsing error: {str(e)}'}, status=400)
        musicxml_path = midi.write('musicxml')

        with open(musicxml_path, 'r') as musicxml_file:
            musicxml_string = musicxml_file.read()

        # The new score meta, including the MusicXML file as `data`
        new_score = flat_api.ScoreCreation(
            title='Hello World',
            privacy='public',
            data=musicxml_string
        )

        try:
            # Try to create the score
            score_response = flat_api.ScoreApi(flat_api_client).create_score(new_score)

            # Print the full response for debugging
            #pprint(score_response)

            # Log the response status code and message
            #print(f"Response Status: {score_response.status_code}")
            #print(f"Response Message: {score_response.message}")

            # Return success response with score URL
            return JsonResponse({
                'status': 'success',
                'message': 'Score created successfully',
                'score_url': score_response.html_url
            }, status=200)

        except ApiException as e:
            print(f"API Exception: {str(e)}")
            # Log the response status code and message in case of failure
            print(f"Response Status: {e.status}")
            print(f"Response Body: {e.body}")

            return JsonResponse({
                'status': 'error',
                'message': f"API error: {str(e)}"
            }, status=500)

    except (ApiException, HTTPError) as e:
        print(f"General Error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def run_script(request):
    if request.method == 'POST':
        try:
            # Save the uploaded audio file to a temporary location
            audio_file = request.FILES['audio_file']
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                for chunk in audio_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            # Path to your Python script
            script_path = '/Users/user/Documents/capstone/scripts/18500-Capstone/main.py'
            print(f"Running script: {script_path}") 

            # Run the script with the audio file path as an argument
            result = subprocess.run(
                ['python', script_path, tmp_file_path, request.user.username if request.user.is_authenticated else None],
                capture_output=True, text=True
            )
            logger.info(f"Script output: {result.stdout}")
            logger.error(f"Script error output: {result.stderr}")
            logger.info(f"Script completed with return code {result.returncode}")

            # Clean up the temporary file
            os.unlink(tmp_file_path)

            if result.returncode != 0:
                return JsonResponse({'status': 'error', 'message': result.stderr}, status=400)

            # Parse JSON output
            #try:
                # Upload to Flat.io
            json = convert_midi(result.stdout.strip())
            return json

                #if not flat_embed_url:
                #    return JsonResponse({'status': 'error', 'message': 'Flat.io upload failed'}, status=500)

                # Save to database
                #sheet = SheetMusic.objects.create(
                #    user=request.user,
                #    title=request.FILES['audio_file'].name,
                #    original_audio=request.FILES['audio_file'],
                #    midi_file=result.stdout, 
                #    #musicxml=data['musicxml'],
                #    flat_embed_url=flat_embed_url  # Store Flat.io embed link
                #)
                #logger.info(f"Created SheetMusic instance ID {sheet.id}")

                #return JsonResponse({ 
                #    'status': 'success',
                #    'sheet_id': sheet.id,
                #    'midi_url': data['midi_url'],
                #  #  'musicxml': data['musicxml'],
                #    'flat_embed_url': flat_embed_url
                #})
                
            #except json.JSONDecodeError:
            #    return JsonResponse({'status': 'error', 'message': 'Invalid script output', 'output': result.stdout}, status=500)

        except Exception as e:
            logger.error(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def run_script3(request):
    if request.method == 'POST':
        try:
            # Save the uploaded audio file to a temporary location
            audio_file = request.FILES['audio_file']
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                for chunk in audio_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            # Path to your Python script
            script_path = '/Users/user/Documents/capstone/scripts/18500-Capstone/MIDI_encoding/midi_gen.py'
            print(f"Running script: {script_path}") 

            # Run the script with the audio file path as an argument
            result = subprocess.run(['python', script_path, tmp_file_path, request.user.username if request.user.is_authenticated else None], capture_output=True, text=True)
            logger.info(f"Script completed with return code {result.returncode}")

            # Clean up the temporary file
            os.unlink(tmp_file_path)

            if result.returncode != 0:
                return JsonResponse({
                    'status': 'error',
                    'message': result.stderr
                }, status=400)

            # Parse JSON output
            try:
                data = json.loads(result.stdout)
                
                if data['status'] != 'success':
                    return JsonResponse({
                        'status': 'error',
                        'message': data.get('error', 'Script failed')
                    }, status=400)
                
                # Save to database
                sheet = SheetMusic.objects.create(
                    user=request.user,
                    title=request.FILES['audio_file'].name,
                    original_audio=request.FILES['audio_file'],
                    midi_file=data['midi_path'], 
                    musicxml=data['musicxml']
                )
                logger.info(f"Created SheetMusic instance ID {sheet.id}")
                
                return JsonResponse({
                    'status': 'success',
                    'sheet_id': sheet.id,
                    'musicxml': data['musicxml']
                })
                
            except json.JSONDecodeError:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid script output',
                    'output': result.stdout
                }, status=500)

        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def run_script2(request):
    print("run_script view called!")
    try: 
        # Replace 'your_script.py' with the path to your Python script
        script_path = '/Users/user/Documents/capstone/scripts/18500-Capstone/MIDI_encoding/midi_gen.py'
        audio_file_path = '/Users/user/Documents/capstone/scripts/18500-Capstone/Audio/Songs/twinkle.m4a'
        print(f"Running script: {script_path}")  # Debugging statement
        
        # Run the script and capture output and errors
        result = subprocess.run(['python', script_path, audio_file_path], capture_output=True, text=True)
        
        # Check for errors
        if result.returncode != 0:
            print(f"Script failed with error: {result.stderr}")  # Debugging statement
            return JsonResponse({'status': 'error', 'message': result.stderr})
        
        output = result.stdout
        print(f"Script output: {output}")  # Debugging statement
        return JsonResponse({'status': 'success', 'output': output})
    except Exception as e:
        print(f"Error: {e}")  # Debugging statement
        return JsonResponse({'status': 'error', 'message': str(e)})

def run_script1(request):
    if request.method == 'POST':
        try:
            # Save the uploaded audio file to a temporary location
            audio_file = request.FILES['audio_file']
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                for chunk in audio_file.chunks():
                    tmp_file.write(chunk)
                tmp_file_path = tmp_file.name

            # Path to your Python script
            script_path = '/Users/user/Documents/capstone/scripts/18500-Capstone/MIDI_encoding/midi_gen.py'
            print(f"Running script: {script_path}") 

            # Run the script with the audio file path as an argument
            midi_data, detected_notes = subprocess.run(['python', script_path, tmp_file_path, request.user.username if request.user.is_authenticated else None], capture_output=True, text=True)

            stream = converter.parse(midi_data)
            musicxml_bytes = io.BytesIO()
            stream.write('musicxml', musicxml_bytes)
            musicxml = musicxml_bytes.getvalue().decode('utf-8')
            
            # Save to database if authenticated
            if request.user.is_authenticated:
                sheet = SheetMusic.objects.create(
                    user=request.user,
                    title=audio_file.name,
                    original_audio=audio_file,
                    musicxml=musicxml
                )
            

            # Clean up the temporary file
            os.unlink(tmp_file_path)

            return JsonResponse({
                'status': 'success',
                'musicxml': musicxml,
                'notes': detected_notes,
                'sheet_id': sheet.id if request.user.is_authenticated else None
            })

            #if result.returncode != 0:
            #    print(f"Script failed with error: {result.stderr}")
            #    return JsonResponse({'status': 'error', 'message': result.stderr})

            #output = result.stdout
            #print(f"Script output: {output}")
            #return JsonResponse({'status': 'success', 'output': output})
        except Exception as e:
            print(f"Error: {e}")
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def homepage_action(request):
    #This creates a user profile form after google OAuth if not created already
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            new_profile = Profile(bio = "Default Bio", user=request.user)
            new_profile.save()
            profile = new_profile

    #recently_added = Product.objects.order_by('-id')[:6]
    #popular_finds = Product.objects.filter(ratings__rating__gt=8).annotate(avg_rating=Avg('ratings__rating')).order_by('-id')[:6]

#    return render(request, 'homepage.html', {'profile': profile, 'recently_added': recently_added, 'popular_finds': popular_finds})
    return render(request, 'base.html', {'profile': profile})

@login_required
def transcriptions_action(request):
    return render(request, 'transcriptions.html')


@login_required
def profile_action(request):
    try: 
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None

    if request.method == 'GET':
        context = {'form': ProfileForm(initial={'bio': profile.bio if profile else None})}
        return render(request, 'userprofile.html', context)
    
    form = ProfileForm(request.POST, request.FILES)
    if not form.is_valid():
        context = {'form': form}
        new = Profile(user=request.user, picture=form.cleaned_data['picture'],
                              content_type=form.cleaned_data['picture'].content_type,
                              bio=form.cleaned_data['bio'])
        new.save()
        return render(request, 'userprofile.html', context)
    
    pic = form.cleaned_data['picture']
    print('Uploaded picture: {} (type={})'.format(pic, type(pic)))

    if profile:
        profile.picture = form.cleaned_data['picture']
        profile.content_type = form.cleaned_data['picture'].content_type
        profile.bio = form.cleaned_data['bio']
        profile.save()
    else:
        profile = Profile(user=request.user, picture=form.cleaned_data['picture'],
                              content_type=form.cleaned_data['picture'].content_type,
                              bio=form.cleaned_data['bio'])
        profile.save()
        
    #products_for_sale = Product.objects.filter(seller=request.user)
    #context = {
    #    'profile': profile,
    #    'form': form,
    #    'products_for_sale': products_for_sale
    #}

    #return render(request, 'userprofile.html', context)
    return

def upload_audio(request):
    if request.method == "POST" and request.FILES.get("audio_file"):
        audio_file = request.FILES["audio_file"]
        saved_file = default_storage.save(f"audio/{audio_file.name}", ContentFile(audio_file.read()))
        
        # Save to the database
        recording = AudioRecording(audio_file=saved_file)
        recording.save()
        
        return JsonResponse({"message": "Audio uploaded successfully!", "file_url": recording.audio_file.url})

    return JsonResponse({"error": "Invalid request"}, status=400)

