
from core import GsmCore

class CallMixin(GsmCore):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clip_enabled = False
    
    def _enable_clip(self):
        """Enable Caller Line Identification Presentation"""
        if not self._clip_enabled:
            try:
                # Enable CLIP: AT+CLIP=1
                self._write("AT+CLIP=1")
                self.get_response(timeout_ms=500)
                self._clip_enabled = True
            except:
                pass  # Silently fail if not supported
    
    def call(self, number):
        self._write("ATD" + number + ";")
    
    def accept_call(self):
        self._write("ATA")
    
    def cut_call(self):
        self._write("ATH")
    
    def loop(self):
        """Check for GSM notifications (incoming calls, etc.)
        
        Returns:
            str: Notification string if available, empty string otherwise
        """
        # Enable CLIP on first loop call
        self._enable_clip()
        
        notification = self.get_response(timeout_ms=200)
        if notification:
            # Clean up the notification
            notification = notification.strip()
            if "RING" in notification:
                print("Incoming call......")
            if notification:
                print(notification)
        return notification if notification else ""
