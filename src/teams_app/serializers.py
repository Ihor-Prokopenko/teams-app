from users.serializers import UserSerializer
from rest_framework import serializers
from .models import Team, Member


class TeamCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['id', 'name']

    def validate(self, attrs):
        existing_team_names = self.context['request'].user.teams.values_list('name', flat=True)
        if attrs['name'] in existing_team_names:
            raise serializers.ValidationError({'name': f'Team with name "{attrs["name"]}" already exists.'})
        return attrs

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class TeamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['id', 'name', 'owner', 'members']
        extra_kwargs = {
            'owner': {'read_only': True},
        }


class MemberCreateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=150)

    class Meta:
        model = Member
        fields = ['email', 'full_name']

    def validate(self, attrs):
        existing_emails = self.context['request'].user.members.values_list('email', flat=True)
        if attrs['email'] in existing_emails:
            raise serializers.ValidationError({'email': f'Member with email "{attrs["email"]}" already exists.'})
        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MemberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Member
        fields = ['id', 'email', 'team', 'user', 'full_name']
        extra_kwargs = {
            'user': {'read_only': True},
        }
