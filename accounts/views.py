from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from .serializers import RegisterSerializer, UserSerializer, UserUpdateSerializer, LoginSerializer
from .models import User


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Қайд муваффақ шуд!",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = (
            User.objects.filter(username=username).first() or
            User.objects.filter(phone=username).first()
        )

        if not user or not user.check_password(password):
            return Response({"error": "Username ё парол нодуруст!"}, status=status.HTTP_401_UNAUTHORIZED)
        if not user.is_active:
            return Response({"error": "Аккаунт фаъол нест!"}, status=status.HTTP_403_FORBIDDEN)

        refresh = RefreshToken.for_user(user)
        return Response({
            "message": "Хуш омадед!",
            "user": UserSerializer(user).data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        })


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if not refresh_token:
                return Response({"error": "Refresh token лозим аст!"}, status=status.HTTP_400_BAD_REQUEST)
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Хориҷ шудед!"})
        except TokenError:
            return Response({"error": "Token нодуруст аст!"}, status=status.HTTP_400_BAD_REQUEST)


class MeView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        return UserUpdateSerializer

    def get_object(self):
        return self.request.user


class TelegramAuthView(APIView):
    """
    Called by the Telegram bot when a user shares their phone number.
    Creates or updates the User with telegram_id + phone.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        from django.conf import settings
        secret = request.headers.get('X-Bot-Secret', '')
        expected = getattr(settings, 'TELEGRAM_BOT_SECRET', '')
        if expected and secret != expected:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)

        telegram_id = request.data.get('telegram_id')
        phone = request.data.get('phone')
        username = request.data.get('username') or str(telegram_id)

        if not telegram_id or not phone:
            return Response(
                {"detail": "telegram_id and phone are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = str(phone).strip()
        if not phone.startswith('+'):
            phone = '+' + phone

        # Find existing user by telegram_id or phone
        user = (
            User.objects.filter(telegram_id=telegram_id).first() or
            User.objects.filter(phone=phone).first()
        )

        if user:
            # Fill in any missing fields
            changed = []
            if not user.telegram_id:
                user.telegram_id = telegram_id
                changed.append('telegram_id')
            if not user.phone:
                user.phone = phone
                changed.append('phone')
            if changed:
                user.save(update_fields=changed)
            return Response({"id": user.id, "success": True, "created": False, "username": user.username})

        # Build a clean username from phone, not from telegram_id
        base = f"user_{phone[-9:].replace('+', '')}"
        final_username = base
        counter = 1
        while User.objects.filter(username=final_username).exists():
            final_username = f"{base}_{counter}"
            counter += 1

        user = User.objects.create_user(
            username=final_username,
            phone=phone,
            telegram_id=telegram_id,
            role=User.Role.CUSTOMER,
            password=None,
        )

        return Response(
            {"id": user.id, "success": True, "created": True, "username": user.username},
            status=status.HTTP_201_CREATED,
        )