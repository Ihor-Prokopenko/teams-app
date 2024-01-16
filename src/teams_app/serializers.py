from rest_framework import serializers
from .models import Team, Member


""" MEMBER SERIALIZERS """


class MemberCreateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=150)

    class Meta:
        model = Member
        fields = ['email', 'full_name']

    def validate(self, attrs):
        """ Validate that the email is not already in use by another user's member. """
        request = self.context.get('request')
        existing_emails = request.user.members.values_list('email', flat=True)
        if attrs['email'] in existing_emails:
            raise serializers.ValidationError({'email': f'Member with email "{attrs["email"]}" already exists.'})
        return attrs

    def create(self, validated_data):
        """ Set the user as creator of the member. """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MemberSerializer(serializers.ModelSerializer):
    class MemberTeamSerializer(serializers.ModelSerializer):

        class Meta:
            model = Team
            fields = ['id', 'name']

    full_name = serializers.CharField(max_length=150, required=False)
    team = MemberTeamSerializer()

    class Meta:
        model = Member
        fields = ['id', 'email', 'team', 'user', 'full_name']
        extra_kwargs = {
            'user': {'read_only': True},
        }


class MemberUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(max_length=150, required=False)

    class Meta:
        model = Member
        fields = ['email', 'full_name', 'team']
        partial = True

    def validate(self, attrs):
        """ Validate that the email is not already in use by another user's member. """
        request = self.context.get('request')
        existing_emails = request.user.members.values_list('email', flat=True).exclude(id=self.instance.id)
        if attrs['email'] in existing_emails:
            raise serializers.ValidationError({'email': f'Member with email "{attrs["email"]}" already exists.'})
        return super().validate(attrs)


""" TEAM SERIALIZERS """


class TeamCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['id', 'name']

    def validate(self, attrs):
        """ Validate that the team name is not already in use by another user's team. """
        request = self.context.get('request')
        existing_team_names = request.user.teams.values_list('name', flat=True)
        if attrs['name'] in existing_team_names:
            raise serializers.ValidationError({'name': f'Team with name "{attrs["name"]}" already exists.'})
        return attrs

    def create(self, validated_data):
        """ Set the user as the owner of the team. """
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class TeamUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Team
        fields = ['name']
        partial = True

    def validate(self, attrs):
        """ Validate that the team name is not already in use by another user's team. """
        request = self.context.get('request')
        existing_emails = request.user.teams.values_list('name', flat=True).exclude(id=self.instance.id)
        if attrs['name'] in existing_emails:
            raise serializers.ValidationError({'name': f'Team with name "{attrs["name"]}" already exists.'})
        return super().validate(attrs)


class TeamSerializer(serializers.ModelSerializer):
    class TeamMemberSerializer(serializers.ModelSerializer):
        class Meta:
            model = Member
            fields = ['id', 'email', 'full_name']

    members = TeamMemberSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'members_count', 'members']
