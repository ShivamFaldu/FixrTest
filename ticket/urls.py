from rest_framework.routers import SimpleRouter

from . import viewsets


router = SimpleRouter(trailing_slash=False)
router.register(r"events", viewsets.EventViewSet)
router.register(r"orders", viewsets.OrderViewSet)
router.register(r"ticket-type", viewsets.TicketTypeViewSet)
urlpatterns = router.urls
