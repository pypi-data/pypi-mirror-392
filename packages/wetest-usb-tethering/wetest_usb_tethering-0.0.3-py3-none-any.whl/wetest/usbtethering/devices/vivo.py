from ..exceptions import SettingsAppException
from .base import BaseDevice


class VivoDevice(BaseDevice):
    """vivo x9"""

    def _open_usb_tethering_page(self):
        """打开到包含`USB 共享网络`开关的页面"""
        self.shell("am start -n com.android.settings/.TetherSettings")
        pid = self.device.app_wait("com.android.settings")
        if pid == 0:
            raise SettingsAppException("Failed to open settings app")
        self.device(text="其他共享方式", className="android.widget.TextView").click(self.timeout)
        self.device(text="通过USB共享网络", className="android.widget.TextView").must_wait(self.timeout)

    def _toggle_usb_tethering_on(self) -> bool:
        """执行`开启 USB 共享`的具体操作"""
        self.device(text="通过USB共享网络").right(resourceId="android:id/checkbox").click()
