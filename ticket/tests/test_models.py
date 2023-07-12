from django.test import TestCase
from django_dynamic_fixture import G, F
import django
django.setup()

from ticket.models import Event, TicketType, Order


class TicketTypeTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.event = G(Event)

    def test_avaialble_tickets(self):
        ticket_type = G(TicketType, name="Test", quantity=5, event=self.event)
        all_tickets = list(ticket_type.tickets.all())

        five_available_tickets = set(ticket_type.available_tickets())

        # book one ticket
        ticket = all_tickets[0]
        ticket.order = G(Order, ticket_type=ticket_type, quantity=1)
        ticket.save()

        four_available_tickets = set(ticket_type.available_tickets())

        self.assertCountEqual(five_available_tickets, all_tickets)
        self.assertCountEqual(four_available_tickets, set(all_tickets) - {ticket})

    def test_save(self):
        """Verifying that the save method creates Ticket(s) upon TicketType creation"""

        ticket_type_1 = G(TicketType, name="Without quantity", event=self.event)
        ticket_type_5 = G(TicketType, name="Test", quantity=5, event=self.event)

        one_ticket = ticket_type_1.tickets.count()
        five_tickets = ticket_type_5.tickets.count()

        self.assertEqual(one_ticket, 1)
        self.assertEqual(five_tickets, 5)


class OrderTest(TestCase):
    def setUp(self):
        self.event = Event.objects.create(name="testEvents", description="test")
        self.ticket_type=TicketType.objects.create(name="testTicket", event=self.event, quantity=10)

    def test_get_number_of_orders_and_cancellation_rate(self):
        order = G(Order, ticket_type=self.ticket_type, quantity=5,cancelled=True)
        G(Order, ticket_type=self.ticket_type, quantity=6,cancelled=False)
        G(Order, ticket_type=self.ticket_type, quantity=6, cancelled=False)
        actual = order.get_number_of_orders_and_cancellation_rate("testEvents")
        expected = {"event":"testEvents", "number_of_orders":3,"cancellation_rate":"33.3%"}
        self.assertEqual(expected,actual)

    def test_get_date_with_highest_cancellation(self):
        order = G(Order, ticket_type=self.ticket_type, quantity=5, cancelled=True)
        G(Order, ticket_type=self.ticket_type, quantity=6, cancelled=True)
        G(Order, ticket_type=self.ticket_type, quantity=6, cancelled=False)
        actual = order.get_date_with_highest_cancellation
        date = order.created_at.strftime('%Y-%m-%d')
        expected = {"date": str(date).split(" ")[0], "number_of_cancelled_ticket": 11}
        self.assertEqual(expected, actual)



    def test_book_tickets(self):
        order = G(Order, ticket_type=F(quantity=5), quantity=3)

        pre_booking_ticket_count = order.tickets.count()
        order.book_tickets()
        post_booking_ticket_count = order.tickets.count()

        with self.assertRaisesRegexp(Exception, r"Order already fulfilled"):
            order.book_tickets()

        self.assertEqual(pre_booking_ticket_count, 0)
        self.assertEqual(post_booking_ticket_count, 3)
