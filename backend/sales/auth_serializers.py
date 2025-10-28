from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
        read_only_fields = ('id', 'is_staff', 'is_superuser')


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        label='Confirm Password'
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2', 'first_name', 'last_name')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Os campos de senha não correspondem."})
        return attrs

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Já existe um usuário com este e-mail.")
        return value

    def create(self, validated_data):
        # CORREÇÃO CRÍTICA:
        # Removido 'password2' pois não é salvo no banco
        validated_data.pop('password2')
        # Pega a senha para o create_user
        password = validated_data.pop('password')
        
        # User.objects.create_user() é a forma correta de criar um usuário,
        # pois ele lida corretamente com o hashing da senha.
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=password,
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError('Deve incluir "email" e "senha".')

        # Tenta encontrar o usuário pelo e-mail
        try:
            user_obj = User.objects.get(email=email)
            username = user_obj.username
        except User.DoesNotExist:
            raise serializers.ValidationError('Credenciais inválidas. Verifique o e-mail e a senha.')

        # Autentica usando o 'username' encontrado e a senha
        user = authenticate(
            request=self.context.get('request'), 
            username=username, 
            password=password
        )

        if not user:
            # CORREÇÃO DE LÓGICA:
            # Se o e-mail foi encontrado, mas a autenticação falhou,
            # o erro está na senha. A mensagem de erro foi corrigida.
            raise serializers.ValidationError('Credenciais inválidas. A senha está incorreta.')

        if not user.is_active:
            raise serializers.ValidationError('Usuário inativo.')

        attrs['user'] = user
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    new_password2 = serializers.CharField(required=True, write_only=True)

    # MELHORIA DE DESIGN:
    # A lógica de validação da senha antiga foi movida da View para o Serializer.
    def validate_old_password(self, value):
        # Pega o usuário do contexto (que deve ser passado pela View)
        user = self.context.get('request').user
        
        if not user.check_password(value):
            raise serializers.ValidationError("A senha antiga está incorreta.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Os campos da nova senha não correspondem."})
        return attrs