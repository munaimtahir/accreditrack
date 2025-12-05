"""
Serializers for accounts app.
"""
from rest_framework import serializers
from .models import User, Role, UserRole


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer for UserRole model."""
    role = RoleSerializer(read_only=True)
    role_id = serializers.UUIDField(write_only=True, required=False)
    department_id = serializers.UUIDField(write_only=True, required=False, allow_null=True)
    department_name = serializers.CharField(source='department.name', read_only=True, required=False)
    
    class Meta:
        model = UserRole
        fields = ['id', 'role', 'role_id', 'department_id', 'department_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model."""
    user_roles = UserRoleSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'is_active', 'is_staff', 'user_roles', 'created_at', 'updated_at', 'password']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Create user with hashed password."""
        password = validated_data.pop('password', None)
        user = User.objects.create_user(password=password, **validated_data)
        return user
    
    def update(self, instance, validated_data):
        """Update user, handling password separately."""
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class UserMeSerializer(serializers.ModelSerializer):
    """Serializer for current user endpoint with roles."""
    roles = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'is_active', 'is_staff', 'roles', 'created_at']
        read_only_fields = ['id', 'email', 'is_staff', 'created_at']
    
    def get_roles(self, obj):
        """Get user roles with department info."""
        user_roles = obj.user_roles.select_related('role', 'department').all()
        return [
            {
                'role': role.role.name,
                'role_display': role.role.get_name_display(),
                'department_id': str(role.department.id) if role.department else None,
                'department_name': role.department.name if role.department else None,
            }
            for role in user_roles
        ]
