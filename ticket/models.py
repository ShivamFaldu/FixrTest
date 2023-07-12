import datetime

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.conf import settings



class Event(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()


class TicketType(models.Model):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(Event, related_name="ticket_types", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, editable=False)

    quantity.help_text = "The number of actual tickets available upon creation"

    def available_tickets(self):
        return self.tickets.filter(order__isnull=True)

    def save(self, *args, **kwargs):
        new = not self.pk
        super().save(*args, **kwargs)
        if new:
            self.tickets.bulk_create([Ticket(ticket_type=self)] * self.quantity)


class Ticket(models.Model):
    ticket_type = models.ForeignKey(TicketType, related_name="tickets", on_delete=models.CASCADE)
    order = models.ForeignKey(
        "ticket.Order", related_name="tickets", default=None, null=True, on_delete=models.SET_NULL
    )


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="orders", on_delete=models.PROTECT)
    ticket_type = models.ForeignKey(TicketType, related_name="orders", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    fulfilled = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)
    cancelled = models.BooleanField(default=False)

    def get_number_of_orders_and_cancellation_rate(selfself,event):
        orders = Order.objects.filter(ticket_type__event__name=event).count()
        cancelled_order = Order.objects.filter(ticket_type__event__name=event, cancelled=True).count()
        if not orders or not cancelled_order :
            raise ValidationError("Could not get orders or cancelled orders")
        try:
            cancellation_percentage = (cancelled_order/orders)*100
        except Exception:
            return
        return {"event":event,"number_of_orders":orders,"cancellation_rate":f"{round(cancellation_percentage,1)}"+"%"}

    @property
    def get_date_with_highest_cancellation(self):
        orders = Order.objects.filter(cancelled=True).order_by("created_at")
        date = orders.first().created_at.strftime('%Y-%m-%d')
        max_date = ""
        created_at=""
        max_quantity = 0
        current_quantity=0
        for order in orders:
            created_at = order.created_at.strftime('%Y-%m-%d')
            if created_at==date:
                current_quantity+=order.quantity
            else:
                if current_quantity>max_quantity:
                    max_quantity=current_quantity
                    max_date = created_at
                current_quantity = order.quantity
                date = created_at
        if current_quantity>max_quantity:
            max_quantity = current_quantity
            max_date = created_at
        return {"date":str(max_date).split(" ")[0], "number_of_cancelled_ticket": max_quantity}

    @transaction.atomic
    def cancel_order(self):
        #followup logic to be added here to modify how many available tickets there will be after cancellation
        current_time=datetime.datetime.utcnow()
        if self.fulfilled:
            if (current_time - self.created_at.replace(tzinfo=None))< datetime.timedelta(minutes=30):
                self.cancelled=True
                self.save()
            else:
                raise ValidationError("You cannot cancel an order after 30 minutes of initial purchase.")
        else:
            raise ValidationError("You cannot cancel an unfulfilled order. Please contact support.")


    def book_tickets(self):
        if self.fulfilled:
            raise Exception("Order already fulfilled")
        qs = self.ticket_type.available_tickets().select_for_update(skip_locked=True)[: self.quantity]
        try:
            with transaction.atomic():
                updated_count = self.ticket_type.tickets.filter(id__in=qs).update(order=self)
                if updated_count != self.quantity:
                    raise Exception
        except Exception:
            return
        self.fulfilled = True
        self.save(update_fields=["fulfilled"])
