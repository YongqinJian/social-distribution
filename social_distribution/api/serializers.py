from rest_framework import serializers

from Profile.models import Author, Post, Comment
from Search.models import FriendRequest

from django.contrib.auth.models import User


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('type', 'id', 'user_name', 'bio', 'location', 'birth_date', 'github')

class PostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('type', 'title', 'id', 'source', 'origin', 'description',
                    'content_type', 'content', 'author', 'categories', 'timestamp',
                    'visibility', 'unlisted')

    # https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = AuthorSerializer(Author.objects.get(pk=data['author'])).data
        #data['comments'] = CommentSerializer(Comment.objects.filter(id__in=data['comments']), many=True).data
        return data

    # https://www.django-rest-framework.org/tutorial/4-authentication-and-permissions/
    def perform_create(self, serializer):
        author = Author.objects.get(user__username=self.request.user.username)
        serializer.save(author=author)

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('type', 'summary', 'sender', 'receiver')

    # https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['sender'] = AuthorSerializer(Author.objects.get(pk=data['sender'])).data
        data['receiver'] = AuthorSerializer(Author.objects.get(pk=data['receiver'])).data
        return data

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('type', 'author', 'content', 'content_type', 'timestamp', 'id')

    # https://stackoverflow.com/questions/41312558/django-rest-framework-post-nested-objects
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = AuthorSerializer(Author.objects.get(pk=data['author'])).data
        return data
