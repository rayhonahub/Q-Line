from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Profile


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Profile
        fields = ['avatar', 'bio', 'birth_date', 'updated_at']
        read_only_fields = ['updated_at']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'phone', 'role',
                  'telegram_id', 'language', 'profile', 'created_at']
        read_only_fields = ['role', 'created_at']


class UserUpdateSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model  = User
        fields = ['email', 'phone', 'language', 'profile']

    def update(self, instance, validated_data):
        # Profile маълумотро ҷудо мекунем
        profile_data = validated_data.pop('profile', {})

        # User навсозӣ
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Profile навсозӣ
        if profile_data:
            for attr, value in profile_data.items():
                setattr(instance.profile, attr, value)
            instance.profile.save()

        return instance


class RegisterSerializer(serializers.ModelSerializer):
    password  = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model  = User
        fields = ['username', 'email', 'phone', 'password', 'password2', 'language']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Паролҳо мувофиқ нестанд!"})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user  


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(help_text="Username ё phone рақам")
    password = serializers.CharField(write_only=True)
