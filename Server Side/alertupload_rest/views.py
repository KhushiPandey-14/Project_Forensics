from alertupload_rest.serializers import UploadAlertSerializer
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from threading import Thread
from django.core.mail import send_mail
import re

# Thread decorator definition
def start_new_thread(function):
    def decorator(*args, **kwargs):
        t = Thread(target = function, args=args, kwargs=kwargs)
        t.daemon = True
        t.start()
    return decorator

# Upload alert
@api_view(['POST'])
def post_alert(request):
    serializer = UploadAlertSerializer(data=request.data)

    if serializer.is_valid():
        serializer.save()
        identify_email_sms(serializer)
    else:
        return JsonResponse({'error': 'Unable to process data!'}, status=400)

    return Response(request.META.get('HTTP_AUTHORIZATION'))

# Identifies if the user provided an email
def identify_email_sms(serializer):
    if re.search(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', serializer.data['alert_receiver']):  
        print("Valid Email")
        send_email(serializer)
    else:
        print("Invalid Email")

# Sends email
@start_new_thread
def send_email(serializer):
    send_mail('Threat Detected!',        #Subject of email
    prepare_alert_message(serializer),   #Body of the image
    'project.defence4@gmail.com',  #Sender's email
    [serializer.data['alert_receiver']],
    #fail_silently=True,)
    fail_silently=False,)

#Prepares the alert message
def prepare_alert_message(serializer):
    image_data = split(serializer.data['image'], ".")
    uuid = image_data[0]
    url = 'http://127.0.0.1:8000/alert' + uuid

    return 'Threat Detected! View alert at ' + url

# Splits string into a list
def split(value, key):
    return str(value).split(key)
