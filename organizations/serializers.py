from rest_framework import serializers
from .models import Organization, Branch, Window
from accounts.serializers import UserSerializer


class WindowSerializer(serializers.ModelSerializer):
    staff_detail = UserSerializer(source='staff', read_only=True)

    class Meta:
        model  = Window
        fields = ['id', 'name', 'staff', 'staff_detail', 'is_active', 'created_at']
        read_only_fields = ['created_at']

    def validate(self, attrs):
        # Staff фақат ин branch-га тааллуқ дошта бошад
        staff = attrs.get('staff')
        if staff and staff.role != 'staff':
            raise serializers.ValidationError({"staff": "Ин корбар staff нест!"})
        return attrs


class BranchSerializer(serializers.ModelSerializer):
    windows = WindowSerializer(many=True, read_only=True)

    class Meta:
        model  = Branch
        fields = ['id', 'name', 'address', 'phone', 'is_active', 'windows', 'created_at']
        read_only_fields = ['created_at']


class OrganizationSerializer(serializers.ModelSerializer):
    branches     = BranchSerializer(many=True, read_only=True)
    owner_detail = UserSerializer(source='owner', read_only=True)

    class Meta:
        model  = Organization
        fields = ['id', 'name', 'slug', 'plan', 'is_active', 'owner', 'owner_detail', 'branches', 'created_at']
        read_only_fields = ['owner', 'plan', 'created_at']

    def validate_slug(self, value):
        if Organization.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Ин slug аллакай мавҷуд аст!")
        return value

    def create(self, validated_data):
        # Owner худкор аз request.user мешавад
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class OrganizationListSerializer(serializers.ModelSerializer):
    """Рӯйхат учун — камтар маълумот"""
    branches_count = serializers.IntegerField(source='branches.count', read_only=True)

    class Meta:
        model  = Organization
        fields = ['id', 'name', 'slug', 'plan', 'is_active', 'branches_count']