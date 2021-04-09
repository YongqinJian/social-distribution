from django.contrib.auth import authenticate
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import JSONParser
from rest_framework import status
from rest_framework.response import Response

from .serializers import AuthorSerializer, PostSerializer, CommentSerializer, LikeSerializer, PostLikeSerializer, CommentLikeSerializer, FriendRequestSerializer
from Profile.models import Author, Post, Comment, PostLike, CommentLike
from Search.models import FriendRequest

import traceback

DEFAULT_HEADERS = {'Referer': 'https://team3-socialdistribution.herokuapp.com/', 'Mode': 'no-cors'}

# https://www.django-rest-framework.org/tutorial/1-serialization/ - was consulted in writing code

@api_view(['GET'])
def get_all_posts(request):
	"""
	Get all public posts
	"""

	posts = Post.objects.filter(visibility=Post.Visibility.PUBLIC, unlisted=False)
	serializer = PostSerializer(posts, many=True)
	return Response(serializer.data)


# Create your views here.
@api_view(['GET'])
def authors(request):
	"""
	Retrieve or update an author.
	"""
	try:
		authors = Author.objects.all()
	except Author.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = AuthorSerializer(authors, many=True)
		return Response(serializer.data)

	else:
		return Response(serializer.errors, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def author_search(request, query):
	"""
	Retrieve or update an author.
	"""
	if request.method == 'GET':
		authors = Author.objects.filter(user__username__contains=query)
		serializer = AuthorSerializer(authors, many=True)
		return Response(serializer.data)

	else:
		return Response(serializer.errors, status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST'])
def author(request, author_id):
	"""
	Retrieve or update an author.
	"""
	try:
		author = Author.objects.get(id=author_id)
	except Author.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = AuthorSerializer(author)
		return Response(serializer.data)

	elif request.method == 'POST':
		# TODO: add authentication
		serializer = AuthorSerializer(author, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE', 'PUT'])
def post(request, author_id, post_id):
	"""
	Create, retrieve, update or delete a post.
	"""

	# Create new post
	if request.method == 'PUT':
		# See if credentials supplied
		if 'password' not in request.data or 'username' not in request.data:
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		else:
			# Log in with those credentials
			username = request.data['username']
			password = request.data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if author_id == str(Author.objects.get(user__username=username).id):
					author = Author.objects.get(id=author_id)
					instance = Post.objects.create(author=author, id=post_id)
					serializer = PostSerializer(instance, data=request.data)

					if serializer.is_valid():
						serializer.save()
						return Response(serializer.data)
				else:
					return Response(status=status.HTTP_401_UNAUTHORIZED)
			else:
				return Response(status=status.HTTP_401_UNAUTHORIZED)


		return Response(status=status.HTTP_401_UNAUTHORIZED)

	# Else, do something with existing post
	try:
		post = Post.objects.get(id=post_id)
	except Post.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		if post.visibility != 'PUBLIC':
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		serializer = PostSerializer(post)
		return Response(serializer.data)

	elif request.method == 'POST':
		serializer = PostSerializer(post, data=request.data, partial=True)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

	elif request.method == 'DELETE':
		if 'password' not in request.data or 'username' not in request.data:
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		else:
			# Log in with those credentials
			username = request.data['username']
			password = request.data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if str(Author.objects.get(user__username=username).id) == str(Post.objects.get(id=post_id).author.id):
					print(author_id)
					print(Post.objects.get(id=post_id).author.id)
					post.delete()
					return Response(status=status.HTTP_204_NO_CONTENT)
				else:
					return Response(status=status.HTTP_401_UNAUTHORIZED)
			else:
				return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
def posts(request, author_id):
	"""
	Get posts from an author or create a post and auto generate an id for it.
	"""

	if request.method == 'GET':
		posts = Post.objects.filter(author__id=author_id, visibility='PUBLIC', unlisted=False).all()
		serializer = PostSerializer(posts, many=True)
		return Response(serializer.data)

	elif request.method == 'POST':
		author = Author.objects.get(id=author_id)
		instance = Post.objects.create(author=author)
		serializer = PostSerializer(instance, data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def friends(request, author_id):
	""" Retrieve friends for an author or create a new one """
	if request.method == 'GET':
		following = Author.objects.get(id=author_id).following.all()
		followers = Author.objects.get(id=author_id).followers.all()
		friends = following & followers

		serializer = AuthorSerializer(friends, many=True)
		return Response(serializer.data)
	else:
		return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'PUT', 'DELETE'])
def friend(request, author_id, friend_id):
	""" Retrieve friends for an author or create a new one """

	try:
		author = Author.objects.get(id=author_id)
		friend = Author.objects.get(id=author_id).following.get(id=friend_id)
	except Author.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		serializer = AuthorSerializer(friend)
		return Response(serializer.data)

	# Add a friend
	elif request.method == 'PUT':
		if 'password' not in request.data or 'username' not in request.data:
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		else:
			# Log in with those credentials
			username = request.data['username']
			password = request.data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if author_id == str(Author.objects.get(user__username=username).id):
					author.friends.add(friend)
					return HttpResponse(status=200)

				else:
					return Response(status=status.HTTP_401_UNAUTHORIZED)
			else:
				return Response(status=status.HTTP_401_UNAUTHORIZED)

		return Response(status=status.HTTP_401_UNAUTHORIZED)

	elif request.method == 'DELETE':

		if request.user is not None and author_id == str(Author.objects.get(user__username=request.user).id):
			author.friends.remove(friend)
			return Response(status=status.HTTP_204_NO_CONTENT)

		elif 'password' not in request.data or 'username' not in request.data:
			return Response(status=status.HTTP_401_UNAUTHORIZED)

		else:
			# Log in with those credentials
			username = request.data['username']
			password = request.data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if author_id == str(Author.objects.get(user__username=username).id):
					author.friends.remove(friend)
					return Response(status=status.HTTP_204_NO_CONTENT)

				else:
					return Response(status=status.HTTP_401_UNAUTHORIZED)
			else:
				return Response(status=status.HTTP_401_UNAUTHORIZED)

	else:
		return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def requests(request, author_id):
	""" Retrieve friend requests for an author"""
	try:
		requests = FriendRequest.objects.filter(receiver_id=author_id).all()
	except:
		return HttpResponse(status=404)


	if request.method == 'GET':
		# Check current logged in user
		if request.user is not None and author_id == str(Author.objects.get(user__username=request.user).id):
			serializer = FriendRequestSerializer(requests, many=True)
			return Response(serializer.data)

		elif 'password' not in request.data or 'username' not in request.data:
			return Response(status=status.HTTP_401_UNAUTHORIZED)

		else:
			username = request.data['username']
			password = request.data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if author_id == str(Author.objects.get(user__username=username).id):
					serializer = FriendRequestSerializer(requests, many=True)
					return Response(serializer.data)
				else:
					return Response(status=status.HTTP_401_UNAUTHORIZED)
			else:
				return Response(status=status.HTTP_401_UNAUTHORIZED)

	else:
		return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET', 'PUT', 'DELETE'])
def request(request, author_id, sender_id):
	""" Retrieve, add or delete friend request for an author"""
	if request.method == 'GET' or request.method == 'DELETE':
		try:
			friend_request = FriendRequest.objects.filter(receiver_id=author_id, sender_id=sender_id).all()[0]
		except:
			return HttpResponse(status=404)

	if request.method == 'GET':
		# Check current logged in user
		if request.user is not None and ( sender_id == str(Author.objects.get(user__username=request.user).id) or author_id == str(Author.objects.get(user__username=request.user).id)):
			serializer = FriendRequestSerializer(friend_request)
			return Response(serializer.data)

		elif 'password' not in request.data or 'username' not in request.data:
			return Response(status=status.HTTP_401_UNAUTHORIZED)

		else:
			username = request.data['username']
			password = request.data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if sender_id == str(Author.objects.get(user__username=username).id):
					serializer = FriendRequestSerializer(friend_request)

					our_host = 'https://team3-socialdistribution.herokuapp.com/'

				# GET the remote friend requests
					for connection in Connection.objects.all():
						url = connection.url + 'service/authors'
						response = requests.get(url, headers=DEFAULT_HEADERS, auth=('CitrusNetwork', 'oranges'))
						for author9 in response.json()['items']:
							if author9['id'] == sender_id:
								request_url = f'{connection.url}service/author/{sender_id}/follow_remote_3/{author_id}/{our_host}'
								# Parse their json here
								# TODO

					return Response(serializer.data)

				else:
					return Response(status=status.HTTP_401_UNAUTHORIZED)

			else:
				return Response(status=status.HTTP_401_UNAUTHORIZED)


	elif request.method == 'PUT':
		# Add authentication here
		data = request.data
		if data['type'].lower() == 'follow' and data['sender']['id'] != None and data['receiver']['id'] == author_id: #remote
			receiver = Author.objects.get(id=author_id)
			# Maybe a function to check if the sender exist on the remote node?
			remote_sender = data["sender"]["id"]
			remote_sender_username = data["sender"]["displayName"]
			# Creating a FriendRequest object:
			# - Receiver is local author object
			# - Remote_sender is the remote author's UUID
			instance = FriendRequest.objects.get_or_create(receiver=receiver, remote_sender=remote_sender, remote_username=remote_sender_username)
			# Add to `remote_followers_uuid` list
			if receiver.remote_followers_uuid != None and remote_sender not in receiver.remote_followers_uuid:
				receiver.remote_followers_uuid += f' {remote_sender}'
			else:
				receiver.remote_followers_uuid = remote_sender
			# Send a following API to the remote author?
			# TODO
			receiver.save()
			return Response({'message':'success'}, status=status.HTTP_200_OK)

		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)


	elif request.method == 'DELETE':
		# Log in with those credentials
		if request.user is not None and sender_id == str(Author.objects.get(user__username=request.user).id):
			friend_request.delete()
			return Response(status=status.HTTP_204_NO_CONTENT)

		elif 'password' not in request.data or 'username' not in request.data:
			return Response(status=status.HTTP_401_UNAUTHORIZED)

		else:
			username = request.data['username']
			password = request.data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if sender_id == str(Author.objects.get(user__username=username).id):
					friend_request.delete()
					return Response(status=status.HTTP_204_NO_CONTENT)


	else:
		return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
def followers(request, author_id):
	if request.method == 'GET':
		followers = Author.objects.get(id=author_id).followers.all()
		serializer = AuthorSerializer(followers, many=True)
		return Response(serializer.data)

@api_view(['GET', 'PUT', 'DELETE'])
def follower(request, author_id, follower_id):
	"""
	Retrieve or delete follower of author, or add user as a follower
	"""

	try:
		author = Author.objects.get(id=author_id)
		follower = Author.objects.get(id=follower_id)
	except Author.DoesNotExist:
		return HttpResponse(status=404)

	if request.method == 'GET':
		if follower in author.followers.all():
			serializer = AuthorSerializer(follower)
			return Response(serializer.data)
		# Not a follower
		return HttpResponse(status=404)

	# Add as follower
	elif request.method == 'PUT':
		if 'password' not in request.data or 'username' not in request.data:
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		else:
			# Log in with those credentials
			username = request.data['username']
			password = request.data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if follower_id == str(Author.objects.get(user__username=username).id):
					author.followers.add(follower)
					follower.following.add(author)
					return HttpResponse(status=200)
				else:
					return Response(status=status.HTTP_401_UNAUTHORIZED)
			else:
				return Response(status=status.HTTP_401_UNAUTHORIZED)

		return Response(status=status.HTTP_401_UNAUTHORIZED)

	elif request.method == 'DELETE':
		# TODO: add authentication
		if 'password' not in request.data or 'username' not in request.data:
			return Response(status=status.HTTP_401_UNAUTHORIZED)
		else:
			# Log in with those credentials
			username = request.data['username']
			password = request.data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if follower_id == str(Author.objects.get(user__username=username).id):
					author.followers.remove(follower)
					follower.following.remove(author)
					return Response(status=status.HTTP_204_NO_CONTENT)
				else:
					return Response(status=status.HTTP_401_UNAUTHORIZED)
			else:
				return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET', 'POST'])
def comments(request, author_id, post_id):
	"""
	Get comments from a post or create a post and auto generate an id for it.
	"""

	if request.method == 'GET':
		post = Post.objects.get(id=post_id)

		if post.visibility != 'PUBLIC':
			return Response(status=status.HTTP_401_UNAUTHORIZED)

		comments = post.comments.all()
		serializer = CommentSerializer(comments, many=True)
		return Response(serializer.data)

	elif request.method == 'POST':
		# TODO: add authentication
		if request.data['type'] == "comment":
			author = Author.objects.get(id=author_id)
			post = Post.objects.get(id=post_id)

			instance = Comment.objects.create(author=author)
			post.comments.add(instance)

			serializer = CommentSerializer(instance, data=request.data)
			if serializer.is_valid():
				serializer.save()
				return Response(serializer.data)
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST'])
def comment(request, author_id, post_id, comment_id):
	"""
	Get comments from a post or create a post and auto generate an id for it.
	"""

	if request.method == 'GET':
		post = Post.objects.get(id=post_id)

		if post.visibility != 'PUBLIC':
			return Response(status=status.HTTP_401_UNAUTHORIZED)

		comment = post.comments.get(id=comment_id)
		serializer = CommentSerializer(comment)
		return Response(serializer.data)

	else:
		return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'POST', 'DELETE'])
def inbox(request, author_id):
	"""
	GET: if authenticated get a list of posts sent to author_id from the inbox
	"""
	if request.method == 'GET':
		# check if the one performing this request is the valid inbox's Author
		if ('password' not in request.data) or ('username' not in request.data):
			try:
				if author_id != str(request.user.author.id):
					return Response(status=status.HTTP_401_UNAUTHORIZED)
			except AttributeError as e:
				return Response(status=status.HTTP_401_UNAUTHORIZED)
			else:
				pass
		# user already authenticated on the web
		if author_id == str(request.user.author.id):
			author = Author.objects.get(id=author_id)
			private_posts = Post.objects.filter(to_author=author_id)
			following = author.following.all()
			friends_posts = Post.objects.filter(visibility='FRIENDS', unlisted=False).filter(author__in=following)
			posts = private_posts | friends_posts
			posts = posts.difference(author.posts_cleared.all()).order_by('-timestamp')
			serializer = PostSerializer(posts, many=True)
			return Response(serializer.data)
		# for example autheticating via Curl
		else:
			username = request.data['username']
			password = request.data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if author_id == str(Author.objects.get(user__username=username).id):
					author = Author.objects.get(id=author_id)
					private_posts = Post.objects.filter(to_author=author_id)
					following = author.following.all()
					friends_posts = Post.objects.filter(visibility='FRIENDS', unlisted=False).filter(author__in=following)
					posts = private_posts | friends_posts
					posts = posts.difference(author.posts_cleared.all()).order_by('-timestamp')
					serializer = PostSerializer(posts, many=True)
					return Response(serializer.data)
				else:
					return Response(status=status.HTTP_401_UNAUTHORIZED)
			return Response(status=status.HTTP_401_UNAUTHORIZED)

	elif request.method == 'POST':
		# Add authentication here
		data = request.data

		# ------ FRIEND REQUEST ------ #

		if data['type'].lower() == 'follow' and data['sender']['id'] != None and data['receiver']['id'] == author_id: #remote
			receiver = Author.objects.get(id=author_id)
			# Maybe a function to check if the sender exist on the remote node?
			remote_sender = data["sender"]["id"]
			remote_sender_username = data["sender"]["displayName"]
			# Creating a FriendRequest object:
			# - Receiver is local author object
			# - Remote_sender is the remote author's UUID
			instance = FriendRequest.objects.get_or_create(receiver=receiver, remote_sender=remote_sender, remote_username=remote_sender_username)
			# Add to `remote_followers_uuid` list
			if receiver.remote_followers_uuid != None and remote_sender not in receiver.remote_followers_uuid:
				receiver.remote_followers_uuid += f' {remote_sender}'
			else:
				receiver.remote_followers_uuid = remote_sender
			# Send a following API to the remote author?
			# TODO
			receiver.save()
			return Response({'message':'success'}, status=status.HTTP_200_OK)

		# ------ POST ------ #

		elif data['type'].lower() == 'post':
			# check if the author is friend/follow you
			receiver = Author.objects.get(id=author_id)
			sender_id = data["author"]["id"]
			try:
				receiver_remote_friends = receiver.remote_friends_uuid.strip().split(" ")
			except:
				receiver_remote_friends = []

			try:
				receiver_remote_followers = receiver.remote_followers_uuid.strip().split(" ")
			except:
				receiver_remote_followers = []
			valid_remote_senders = receiver_remote_followers + receiver_remote_friends
			# REMOTE SENDER
			if sender_id in valid_remote_senders:
				try:
					if data["visibility"].upper() in "FRIENDS" + "PRIVATE" and author_id == data["receiver"]:
						instance = Post(
							title = data["title"],
							id = data["id"],
							remote_url = data["remote_url"],
							source = data["source"],
							origin = data["origin"],
							description = data["description"],
							contentType = data["contentType"],
							content = data["content"],
							remote_author_id = data["author"]["id"],
							remote_author_displayName = data["author"]["displayName"],
							to_author = receiver,
							timestamp = data["timestamp"],
							visibility = data["visibility"],
							unlisted = data["unlisted"],
						)
						instance.categories.set(data["categories"])
						instance.save()
						return Response({'message':'success'}, status=status.HTTP_200_OK)
					else:
						return Response({"message": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
				except Exception:
					traceback.print_exc()
					return Response({"message":"something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

			# LOCAL SENDER
		elif sender_id in [str(x) for x in receiver.following.all().values('id')]:
				sender_local = Author.objects.get(id=sender_id)
				try:
					if data["visibility"].upper() in "FRIENDS" + "PRIVATE" and author_id == data["receiver"]:
						instance = Post(
							title = data["title"],
							id = data["id"],
							source = data["source"],
							origin = data["origin"],
							description = data["description"],
							contentType = data["contentType"],
							content = data["content"],
							author = sender_local,
							to_author = receiver,
							timestamp = data["timestamp"],
							visibility = data["visibility"],
							unlisted = data["unlisted"],
						)
						instance.categories.set(data["categories"])
						instance.save()
						return Response({'message':'success'}, status=status.HTTP_200_OK)
					else:
						return Response({"message": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)
				except Exception as e:
					return Response({"message":e}, status=status.HTTP_400_BAD_REQUEST)
			# UNAUTHORIZED or SOMETHING WRONG
			else:
				return Response({"message": "something went wrong"}, status=status.HTTP_400_BAD_REQUEST)

		else:
			return Response(status=status.HTTP_400_BAD_REQUEST)

	elif request.method == 'DELETE':
		if ('password' not in request.data) or ('username' not in request.data):
			try:
				if author_id != str(request.user.author.id):
					return Response(status=status.HTTP_401_UNAUTHORIZED)
			except AttributeError as e:
				return Response(status=status.HTTP_401_UNAUTHORIZED)
			else:
				pass
		if author_id == str(request.user.author.id):
			author = Author.objects.get(id=author_id)
			private_posts = Post.objects.filter(to_author=author_id)
			following = author.following.all()
			friends_posts = Post.objects.filter(visibility='FRIENDS', unlisted=False).filter(author__in=following)
			posts = private_posts | friends_posts
			friend_requests = FriendRequest.objects.filter(receiver=author)

			author.posts_cleared.add(*posts)
			author.friend_requests_cleared.add(*friend_requests)
			posts = posts.difference(author.posts_cleared.all())
			friend_requests = friend_requests.difference(author.friend_requests_cleared.all())

			return Response(status=status.HTTP_204_NO_CONTENT)
		else:
			# Log in with those credentials
			username = request.data['username']
			password = request.data['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if follower_id == str(Author.objects.get(user__username=username).id):
					author = Author.objects.get(id=author_id)
					private_posts = Post.objects.filter(to_author=author_id)
					following = author.following.all()
					friends_posts = Post.objects.filter(visibility='FRIENDS', unlisted=False).filter(author__in=following)
					posts = private_posts | friends_posts
					friend_requests = FriendRequest.objects.filter(receiver=author)

					author.posts_cleared.add(*posts)
					author.friend_requests_cleared.add(*friend_requests)
					posts = posts.difference(author.posts_cleared.all())
					friend_requests = friend_requests.difference(author.friend_requests_cleared.all())

					return Response(status=status.HTTP_204_NO_CONTENT)
				else:
					return Response(status=status.HTTP_401_UNAUTHORIZED)
			else:
				return Response(status=status.HTTP_401_UNAUTHORIZED)


@api_view(['GET'])
def post_likes(request, author_id, post_id):
	if request.method == 'GET':
		likes = PostLike.objects.filter(post_id=post_id)
		serializer = PostLikeSerializer(likes, many=True)
		return Response(serializer.data)

	else:
		return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def comment_likes(request, author_id, post_id, comment_id):
	if request.method == 'GET':
		likes = CommentLike.objects.filter(post_id=post_id, comment_id=comment_id)
		serializer = CommentLikeSerializer(likes, many=True)
		return Response(serializer.data)

	else:
		return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['GET'])
def liked(request, author_id):
	if request.method == 'GET':
		post_likes = PostLike.objects.filter(author_id=author_id).all()
		post_serializer = PostLikeSerializer(post_likes, many=True)

		comment_likes = CommentLike.objects.filter(author_id=author_id).all()
		comment_serializer = CommentLikeSerializer(comment_likes, many=True)

		# Very hacky
		likes = list(post_serializer.data) + list(comment_serializer.data)
		return Response(likes)

	else:
		return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
