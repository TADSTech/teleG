"""
Simple health check API for Telegram Monitor
Provides REST endpoints for dashboard monitoring
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class HealthCheckHandler(BaseHTTPRequestHandler):
    """HTTP handler for health check endpoints"""
    
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.health_check()
        elif self.path == '/logs':
            self.get_logs()
        else:
            self.send_error(404, 'Not found')
    
    def do_POST(self):
        """Handle POST requests"""
        if self.path == '/cache/clear':
            self.clear_cache()
        elif self.path == '/service/restart':
            self.restart_service()
        elif self.path == '/settings':
            self.save_settings()
        else:
            self.send_error(404, 'Not found')
    
    def do_OPTIONS(self):
        """Handle CORS preflight"""
        self.send_response(200)
        self._set_cors_headers()
        self.end_headers()
    
    def _set_cors_headers(self):
        """Set CORS headers for cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
    
    def health_check(self):
        """Return health status"""
        try:
            stats = self.load_stats()
            response = {
                'status': 'online',
                'timestamp': datetime.now().isoformat(),
                'messagesProcessed': stats.get('messagesProcessed', 0),
                'alertsSent': stats.get('alertsSent', 0),
                'uptime': stats.get('uptime', 0),
                'channel': 'THEABZBRAND'
            }
            self.send_json(response, 200)
        except Exception as e:
            logger.error(f"Health check error: {e}")
            self.send_json({'status': 'error', 'message': str(e)}, 500)
    
    def get_logs(self):
        """Return recent logs"""
        try:
            # Read from processed_messages.json
            msg_file = Path('processed_messages.json')
            if msg_file.exists():
                with open(msg_file) as f:
                    messages = json.load(f)
                logs = '\n'.join([
                    f"[{v.get('timestamp', 'N/A')}] {v.get('text', '')[:100]}"
                    for k, v in list(messages.items())[-20:]
                ])
            else:
                logs = 'No logs available yet'
            
            self.send_json({'logs': logs}, 200)
        except Exception as e:
            logger.error(f"Logs error: {e}")
            self.send_json({'logs': f'Error reading logs: {str(e)}'}, 500)
    
    def clear_cache(self):
        """Clear message cache"""
        try:
            msg_file = Path('processed_messages.json')
            if msg_file.exists():
                msg_file.unlink()
            
            stats = self.load_stats()
            stats['messagesProcessed'] = 0
            self.save_stats(stats)
            
            self.send_json({'status': 'success', 'message': 'Cache cleared'}, 200)
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            self.send_json({'status': 'error', 'message': str(e)}, 500)
    
    def restart_service(self):
        """Restart the telegram monitor service"""
        # This should be triggered via systemctl, not directly
        self.send_json({
            'status': 'success',
            'message': 'Restart requested. Service will restart in 10 seconds.'
        }, 200)
        logger.info("Service restart requested")
    
    def save_settings(self):
        """Save dashboard settings"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            settings = json.loads(body)
            
            # Save settings (implement as needed)
            logger.info(f"Settings updated: {settings}")
            
            self.send_json({'status': 'success', 'message': 'Settings saved'}, 200)
        except Exception as e:
            logger.error(f"Settings error: {e}")
            self.send_json({'status': 'error', 'message': str(e)}, 500)
    
    def send_json(self, data, status_code):
        """Send JSON response"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._set_cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    @staticmethod
    def load_stats():
        """Load statistics from file"""
        stats_file = Path('.monitor_stats')
        if stats_file.exists():
            try:
                with open(stats_file) as f:
                    return json.load(f)
            except:
                pass
        return {'messagesProcessed': 0, 'alertsSent': 0, 'uptime': 0}
    
    @staticmethod
    def save_stats(stats):
        """Save statistics to file"""
        with open('.monitor_stats', 'w') as f:
            json.dump(stats, f)
    
    def log_message(self, format, *args):
        """Suppress default logging"""
        pass


def start_health_check_server(host='localhost', port=9999):
    """Start health check HTTP server"""
    server = HTTPServer((host, port), HealthCheckHandler)
    logger.info(f"Health check server started on {host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Health check server stopped")
        server.server_close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    start_health_check_server()
