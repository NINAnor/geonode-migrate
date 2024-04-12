from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers, status, permissions

from geonode.base.models import ResourceBase

from django.contrib.auth import get_user_model

User = get_user_model()

class UserPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class ChangeResourceOwnershipSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    resource_id = serializers.IntegerField(required=True)


class UpdateUserPassword(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = UserPasswordSerializer(data=request.data)
        if serializer.is_valid():
            u = User.objects.get(username=serializer.data['username'])
            u.set_password(serializer.data['password'])
            u.save()
            return Response({'success': True})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateResourceOwner(APIView):
    permission_classes = [permissions.IsAdminUser]

    def post(self, request):
        serializer = ChangeResourceOwnershipSerializer(data=request.data)
        if serializer.is_valid():
            u = User.objects.get(username=serializer.data['username'])
            r = ResourceBase.objects.get(id=serializer.data['resource_id'])
            r.owner = u
            r.save()
            return Response({'success': True})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)