from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import date

from .models import Flight, Booking, Profile


class FlightSerializer(serializers.ModelSerializer):
	class Meta:
		model = Flight
		fields = ['destination', 'time', 'price', 'id']

# modify this to return the destination instead of the id, and return the flight, date and id
class BookingSerializer(serializers.ModelSerializer):
	flight = serializers.SlugRelatedField(
			read_only=True,
			slug_field='destination'
		)

	class Meta:
		model = Booking
		fields = ['flight', 'date', 'id']

# Modify this to return more info
class BookingDetailsSerializer(serializers.ModelSerializer):
	total = serializers.SerializerMethodField() # total cost of flight for all passengers
	#flight = serializers.SerializerMethodField() # detailed flight info
	flight = FlightSerializer() # when using the Flight serializer, it'll auto feed the flight id since it's a foreign key in the Model relationship -- no need to create a function override

	class Meta:
		model = Booking
		#fields = ['flight', 'date', 'passengers', 'id'] # original fields
		fields = ['total', 'flight', 'date', 'id', 'passengers']

	def get_total(self, object):
		return object.flight.price * object.passengers

	# function override is not required since we already have the fligh tid which is a foreign key to the Flight model
	#def get_flight(self, object):
	#	info = Flight.objects.filter(bookings=object.id).first()
	#	return FlightSerializer(instance=info, read_only=True).data


class AdminUpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['date', 'passengers']


class UpdateBookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['passengers']


class RegisterSerializer(serializers.ModelSerializer):
	password = serializers.CharField(write_only=True)
	class Meta:
		model = User
		fields = ['username', 'password', 'first_name', 'last_name']

	def create(self, validated_data):
		username = validated_data['username']
		password = validated_data['password']
		first_name = validated_data['first_name']
		last_name = validated_data['last_name']
		new_user = User(username=username, first_name=first_name, last_name=last_name)
		new_user.set_password(password)
		new_user.save()
		return validated_data

# Override what info is returned from a User model
class UserInfoSerializer(serializers.ModelSerializer):
	class Meta:
		model = User	
		fields = ['first_name', 'last_name']

class ProfileSerializer(serializers.ModelSerializer):

	#first_name = serializers.SerializerMethodField()
	#last_name = serializers.SerializerMethodField()
	user = serializers.SerializerMethodField()
	past_bookings = serializers.SerializerMethodField()
	tier = serializers.SerializerMethodField()
	
	class Meta:
		model = Profile
		#fields = ['user', 'miles', 'first_name', 'last_name'] # original order
		fields = ['user', 'miles', 'past_bookings', 'tier']

	#def get_first_name(self, object):
	#	return object.user.first_name

	#def get_last_name(self, object):
	#	return object.user.last_name

	def get_user(self, object):
		# The test expected the first & last names to be fed through a dictionary owned by a user object, so had to override the fields using a new class above
		return UserInfoSerializer(instance=object.user, read_only=True).data

	# return bookings that have already passed (old)
	def get_past_bookings(self, object):
		# answer found here: https://stackoverflow.com/questions/25312987/django-rest-framework-limited-queryset-for-nested-modelserializer
		bookings = Booking.objects.filter(user=object.user,date__lt=date.today())
		serializer = BookingSerializer(instance=bookings, many=True)
		return serializer.data

	# returns the tier based on the miles accumulated
	def get_tier(self, object):
		if (object.miles >= 0 and object.miles < 10000):
			return "Blue"
		elif (object.miles >= 10000 and object.miles < 60000):
			return "Silver"
		elif (object.miles >= 60000 and object.miles < 100000):
			return "Gold"
		elif (object.miles >= 100000):
			return "Platinum"
		else:
			return "Blue"
