from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import date

from .models import Flight, Booking, Profile


class FlightSerializer(serializers.ModelSerializer):
	class Meta:
		model = Flight
		fields = ['destination', 'time', 'price', 'id']


class BookingSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['flight', 'date', 'id']


class BookingDetailsSerializer(serializers.ModelSerializer):
	class Meta:
		model = Booking
		fields = ['flight', 'date', 'passengers', 'id']


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


"""
class SlugRelatedBookingField(serializers.SlugRelatedField):
	def get_queryset(self):
		queryset = self.queryset
		if hasattr(self.root, 'booking_id'):
			queryset = queryset.filter(date__lt=date.today(),user=self.root.user)
		return queryset
"""

class ProfileSerializer(serializers.ModelSerializer):

	first_name = serializers.SerializerMethodField()
	last_name = serializers.SerializerMethodField()
	#past_bookings = BookingSerializer(queryset=Booking.objects.filter(user=value.user,date__lt=date.today()))
	past_bookings = serializers.SerializerMethodField()
	tier = serializers.SerializerMethodField()
	
	class Meta:
		model = Profile
		#fields = ['user', 'miles', 'first_name', 'last_name'] # original order
		fields = ['first_name', 'last_name', 'miles', 'past_bookings', 'tier']

	def get_first_name(self, object):
		return object.user.first_name

	def get_last_name(self, object):
		return object.user.last_name

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
		elif (object.miles > 10000 and object.miles < 60000):
			return "Silver"
		elif (object.miles > 60000 and object.miles < 100000):
			return "Gold"
		else:
			return "Platinum"

"""
assigned_to = serializers.SlugRelatedField(
   queryset=User.objects.all(),
   slug_field='username',
   style={'base_template': 'input.html'}
)
"""