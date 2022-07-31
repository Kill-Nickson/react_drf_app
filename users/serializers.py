import sys
from django.core import exceptions

from rest_framework import serializers
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

from django.contrib.auth import password_validation as validators
from django.contrib.auth.models import update_last_login
from django.core.exceptions import ObjectDoesNotExist

from users.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'created_at', 'updated_at']
        read_only_field = ['is_active', 'created_at', 'updated_at']


class LoginSerializer(TokenObtainPairSerializer):

    def create(self, validated_data):
        """Empty realization of the BaseSerializer abstract method"""
        pass

    def update(self, instance, validated_data):
        """Empty realization of the BaseSerializer abstract method"""
        pass

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['user'] = UserSerializer(self.user).data
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, self.user)

        return data


class RegisterSerializer(UserSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True, required=True)
    email = serializers.EmailField(required=True, write_only=True, max_length=128)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_active', 'created_at', 'updated_at']

    def create(self, validated_data):
        try:
            user = User.objects.get(email=validated_data['email'])
        except ObjectDoesNotExist:
            user = User.objects.create_user(**validated_data)
        return user

    def validate(self, data):
        user = User(**data)
        password = data.get('password')

        errors = dict()
        try:
            validators.validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
            errors['password'] = list(e.messages)

        if errors:
            raise serializers.ValidationError(errors)

        return super().validate(data)
