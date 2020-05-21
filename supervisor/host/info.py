"""Info control for host."""
import asyncio
import logging
from typing import Optional

from ..coresys import CoreSysAttributes
from ..exceptions import (
    DBusError,
    DBusNotConnectedError,
    HostError,
    HostNotSupportedError,
)

_LOGGER: logging.Logger = logging.getLogger(__name__)


class InfoCenter(CoreSysAttributes):
    """Handle local system information controls."""

    def __init__(self, coresys):
        """Initialize system center handling."""
        self.coresys = coresys

    @property
    def hostname(self) -> Optional[str]:
        """Return local hostname."""
        return self.sys_dbus.hostname.hostname

    @property
    def chassis(self) -> Optional[str]:
        """Return local chassis type."""
        return self.sys_dbus.hostname.chassis

    @property
    def deployment(self) -> Optional[str]:
        """Return local deployment type."""
        return self.sys_dbus.hostname.deployment

    @property
    def kernel(self) -> Optional[str]:
        """Return local kernel version."""
        return self.sys_dbus.hostname.kernel

    @property
    def operating_system(self) -> Optional[str]:
        """Return local operating system."""
        return self.sys_dbus.hostname.operating_system

    @property
    def cpe(self) -> Optional[str]:
        """Return local CPE."""
        return self.sys_dbus.hostname.cpe

    async def get_dmesg(self) -> bytes:
        """Return host dmesg output."""
        proc = await asyncio.create_subprocess_shell(
            "dmesg", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.STDOUT
        )

        # Get kernel log
        try:
            stdout, _ = await proc.communicate()
        except OSError as err:
            _LOGGER.error("Can't read kernel log: %s", err)
            raise HostError()

        return stdout

    async def update(self):
        """Update properties over dbus."""
        _LOGGER.info("Update local host information")
        try:
            await self.sys_dbus.hostname.update()
        except DBusError:
            _LOGGER.warning("Can't update host system information!")
        except DBusNotConnectedError:
            _LOGGER.error("No hostname D-Bus connection available")
            raise HostNotSupportedError() from None
