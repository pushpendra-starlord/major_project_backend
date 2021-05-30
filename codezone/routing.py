from channels.routing import ProtocolTypeRouter, URLRouter
import notification.routing
import chat.routing
from authentication.middleware import TokenAuthMiddlewareStack

application = ProtocolTypeRouter({
    'websocket': TokenAuthMiddlewareStack(
        URLRouter(
            notification.routing.websocket_urlpatterns+
            chat.routing.websocket_urlpatterns
        )
    )
    
})