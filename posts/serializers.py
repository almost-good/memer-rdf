from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers
from .models import Post
from votes.models import Vote


class PostSerializer(serializers.ModelSerializer):
    """
    Serializer for the Post model.
    """

    owner = serializers.ReadOnlyField(source='owner.username')
    is_owner = serializers.SerializerMethodField()
    profile_id = serializers.ReadOnlyField(source='owner.profile.id')
    profile_image = serializers.ReadOnlyField(source='owner.profile.image.url')
    vote_id = serializers.SerializerMethodField()
    vote_value = serializers.SerializerMethodField()
    comments_count = serializers.ReadOnlyField()
    vote_count = serializers.ReadOnlyField()
    vote_score = serializers.ReadOnlyField()

    def validate_image(self, value):
        if value.size > 2 * 1024 * 1024:
            raise serializers.ValidationError(
                "Image size exceeds 2MB."
            )
        if (
            value.image.width > 4096
            or value.image.height > 4096
        ):
            raise serializers.ValidationError(
                "Image dimensions exceed 4096x4096."
            )
        return value

    def get_is_owner(self, obj):
        request = self.context['request']
        return request.user == obj.owner

    def _get_user_vote(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            post_ct = ContentType.objects.get_for_model(Post)
            vote = Vote.objects.filter(
                owner=user, content_type=post_ct, object_id=obj.id
            ).first()
            return vote
        return None

    def get_vote_id(self, obj):
        vote = self._get_user_vote(obj)
        return vote.id if vote else None  # type: ignore

    def get_vote_value(self, obj):
        vote = self._get_user_vote(obj)
        return vote.value if vote else None

    class Meta:
        model = Post
        fields = [
            'id',
            'owner',
            'is_owner',
            'profile_id',
            'profile_image',
            'created_at',
            'updated_at',
            'title',
            'image',
            'comments_count',
            'vote_id',
            'vote_value',
            'vote_count',
            'vote_score',
        ]
