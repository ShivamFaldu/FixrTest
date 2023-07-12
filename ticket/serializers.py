from django.core.exceptions import ValidationError
from rest_framework import serializers

from . import models


class TicketTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.TicketType
        fields = ("id", "name")


class EventSerializer(serializers.ModelSerializer):
    ticket_types = TicketTypeSerializer(many=True)

    class Meta:
        model = models.Event
        fields = ("id", "name", "description", "ticket_types")


class OrderSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        #this update method was only designed to update cancellation and nothing else
        if instance.cancelled:
            raise ValidationError("This order has already been cancelled.")
        if instance.quantity != validated_data["quantity"]:
            raise ValidationError("Cannot update this field at the moment")
        if instance.ticket_type != validated_data["ticket_type"]:
            raise ValidationError("Cannot update this field at the moment")
        if validated_data["cancelled"]:
            instance.cancel_order
        return instance

    class Meta:
        model = models.Order
        fields = ("id", "ticket_type", "quantity", "cancelled", "created_at")
