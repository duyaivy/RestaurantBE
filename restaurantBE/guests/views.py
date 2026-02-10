from django.shortcuts import render
from rest_framework import generics
from .models import Guest
from .serializers import GuestSerializer

# Create your views here.
class GuestListCreateView(generics.ListCreateAPIView):
    queryset = Guest.objects.all()
    serializer_class = GuestSerializer