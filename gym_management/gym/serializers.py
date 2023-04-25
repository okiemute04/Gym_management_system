from rest_framework import serializers
import datetime
from time import timezone
from .models import Invoice, InvoiceLine, Membership, Checkin


class InvoiceLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvoiceLine
        fields = ('id', 'description', 'amount')


class InvoiceSerializer(serializers.ModelSerializer):
    lines = InvoiceLineSerializer(many=True, read_only=True)

    class Meta:
        model = Invoice
        fields = ('id', 'date', 'status', 'description', 'amount', 'lines')


class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ('id', 'user', 'state', 'credits', 'start_date', 'end_date')


class CheckinSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Checkin
        fields = ('id', 'user', 'membership', 'timestamp')

    def validate_membership(self, value):
        if value.end_date and value.end_date < timezone.now().date():
            raise serializers.ValidationError("Membership has expired.")
        return value


class CheckinCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkin
        fields = ('user', 'membership')

    def validate(self, data):
        user = data.get('user')
        membership = data.get('membership')
        if not membership:
            raise serializers.ValidationError("Membership is required.")
        if membership.state == 'canceled':
            raise serializers.ValidationError("Cannot check in with a canceled membership.")
        if membership.end_date and membership.end_date < datetime.datetime.now().date():
            raise serializers.ValidationError("Membership has expired.")
        if membership.credits <= 0:
            raise serializers.ValidationError("No credits available.")
        return data
