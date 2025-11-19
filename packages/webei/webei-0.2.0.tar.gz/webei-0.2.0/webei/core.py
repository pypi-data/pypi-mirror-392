from flask import Blueprint, send_from_directory, render_template, current_app
from flask_socketio import SocketIO
import os
import json

class Webei:
    def __init__(self, app=None):
        self.app = app
        self.socketio = SocketIO(app)
        self.event_handlers = {}
        self._element_proxy_cache = {}
        self.assets_to_load = []

        if app:
            self.init_app(app)

    def init_app(self, app):
        self.socketio.init_app(app)
        self.socketio.on_event('webei_event', self.handle_webei_event)

        # The directory containing this file
        webei_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Path to the static and prebuilt directories
        static_folder = os.path.join(webei_dir, 'static')
        prebuilt_folder = os.path.join(webei_dir, 'prebuilt')

        webei_bp = Blueprint(
            'webei', __name__,
            static_folder=static_folder,
            static_url_path='/_webei/static'
        )
        
        # Route to serve prebuilt assets (CSS, Animations)
        @webei_bp.route('/_webei/prebuilt/<path:filename>')
        def serve_prebuilt(filename):
            return send_from_directory(prebuilt_folder, filename)

        app.register_blueprint(webei_bp)

    def on(self, event_name):
        def decorator(f):
            self.event_handlers[event_name] = f
            return f
        return decorator

    def handle_webei_event(self, data):
        event_name = data.get('event_name')
        handler = self.event_handlers.get(event_name)
        if handler:
            handler(element_id=data.get('element_id'), payload=data)

    def element(self, element_id):
        if element_id not in self._element_proxy_cache:
            self._element_proxy_cache[element_id] = self._ElementProxy(element_id, self.socketio)
        return self._element_proxy_cache[element_id]

    def load_css(self, style, settings={}, ignore=False):
        self.assets_to_load.append({
            "type": "css",
            "name": style,
            "settings": settings,
            "ignore": ignore
        })

    def load_anim(self, style, settings={}, ignore=False):
        self.assets_to_load.append({
            "type": "animations",
            "name": style,
            "settings": settings,
            "ignore": ignore
        })

    def render(self, template_name, **context):
        # Render the user's template first
        html_content = render_template(template_name, **context)

        # Prepare the asset loading script
        script_content = ""
        if self.assets_to_load:
            assets_json = json.dumps(self.assets_to_load)
            script_content = f"""
<script>
document.addEventListener('DOMContentLoaded', () => {{
    if (window.webei && window.webei.loadAssets) {{
        window.webei.loadAssets({assets_json});
    }} else {{
        console.error('Webei assets could not be loaded. webei.js might be missing or failed to load.');
    }}
}});
</script>
"""
            # Clear the list for the next request cycle
            self.assets_to_load = []

        # Inject Socket.IO, webei.js, and the asset loader script
        socket_io_script = '<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>'
        webei_script = '<script src="/_webei/static/webei.js"></script>'
        
        all_scripts = f"\n{socket_io_script}\n{webei_script}\n{script_content}\n</body>"

        # Replace the closing body tag with our scripts and the tag itself
        if '</body>' in html_content:
            html_content = html_content.replace('</body>', all_scripts, 1)
        else:
            # If no body tag, just append them.
            html_content += f"\n{socket_io_script}\n{webei_script}\n{script_content}"

        return html_content

    class _ElementProxy:
        def __init__(self, element_id, socketio):
            self.element_id = element_id
            self.socketio = socketio

        def _emit_command(self, command, payload):
            self.socketio.emit('webei_command', {
                'element_id': self.element_id,
                'command': command,
                'payload': payload
            })

        def set_text(self, text):
            self._emit_command('set_text', text)

        def set_attribute(self, attribute, value):
            self._emit_command('set_attribute', {'attribute': attribute, 'value': value})
        
        def add_class(self, class_name):
            self._emit_command('add_class', class_name)

        def remove_class(self, class_name):
            self._emit_command('remove_class', class_name)

        def set_style(self, style, value):
            self._emit_command('set_style', {'style': style, 'value': value})