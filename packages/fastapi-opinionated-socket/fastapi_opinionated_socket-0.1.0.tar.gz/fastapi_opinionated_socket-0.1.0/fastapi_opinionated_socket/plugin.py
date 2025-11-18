from fastapi_opinionated.registry.plugin_store import PluginRegistryStore
from socketio import AsyncServer, ASGIApp
from fastapi_opinionated.shared.base_plugin import BasePlugin
from fastapi_opinionated.decorators.app_cmd import AppCmd
from fastapi_opinionated.shared.logger import ns_logger
from fastapi_opinionated.exceptions.plugin_exception import PluginException

logger = ns_logger("SocketPlugin")
class SocketPlugin(BasePlugin):
    public_name = "socket"
    command_name = "socket.enable"
    target_class = AsyncServer
    required_config = True
    def __init__(self):
        self.handlers = {}
    
    @staticmethod
    @AppCmd("socket.enable")
    def _internal(app, fastapi_app, *args, **kwargs):
        """
        Initialize and mount a Socket.IO ASGI application onto a FastAPI application.
        Parameters
        ----------
        app: Any
            Host application or plugin manager (not used directly by this function but
            provided by the plugin system).
        fastapi_app: fastapi.FastAPI
            The FastAPI application instance on which the Socket.IO ASGI app will be mounted.
        *args: tuple
            Positional arguments forwarded to socketio.AsyncServer.
        **kwargs: dict
            Keyword arguments forwarded to socketio.AsyncServer. Special handling for:
              - socketio_path (str): Optional mount path for the Socket.IO ASGI app.
                Defaults to "socket.io". If provided, it is removed from kwargs and
                normalized to ensure a leading '/' (e.g. "socket.io" -> "/socket.io").
        Returns
        -------
        socketio.AsyncServer
            The initialized AsyncServer instance.
        Raises
        ------
        RuntimeError
            If any error occurs during initialization or mounting. The original
            exception is logged and wrapped in a RuntimeError.
        Behavior / Side effects
        ----------------------
        - Creates a namespaced logger ("SocketPlugin") and logs initialization start/stop.
        - Instantiates socketio.AsyncServer using the provided *args and **kwargs.
        - Normalizes and consumes the 'socketio_path' option from kwargs.
        - Creates an ASGIApp with the AsyncServer and mounts it onto fastapi_app at
          the normalized socketio_path.
        - Returns the created AsyncServer instance on success.
        """
        
        try:
            logger.info("Enabling SocketPlugin...")
            sio = AsyncServer(*args, **kwargs)

            socketio_path = kwargs.pop("socketio_path", "socket.io")
            socketio_path = f"/{socketio_path.strip('/')}"
            
            socket_app = ASGIApp(socketio_server=sio,socketio_path=socketio_path)
            fastapi_app.mount(socketio_path, socket_app)
            
            logger.info("SocketPlugin enabled successfully.")
            return sio
        except Exception as e:
            raise PluginException("SocketPlugin", cause=e)
        
    # ----------------------
    # Lifecycle hook
    # ----------------------
    def on_controllers_loaded(self, app, fastapi_app):
        self.handlers = PluginRegistryStore.get(self.public_name).get("socket_event_handlers", [])
    
    def on_ready(self, app, fastapi_app, sio):

        for item in self.handlers:
            event = item["event"]
            handler = item["handler"]
            namespace = item["namespace"]

            if namespace:
                sio.on(event, namespace=namespace)(handler)
                logger.info(f"Registered '{event}' on namespace '{namespace}'")
            else:
                sio.on(event)(handler)
                logger.info(f"Registered '{event}'")
    
    async def on_shutdown_async(self, app, fastapi_app, plugin_api: AsyncServer):
        await plugin_api.shutdown()
    