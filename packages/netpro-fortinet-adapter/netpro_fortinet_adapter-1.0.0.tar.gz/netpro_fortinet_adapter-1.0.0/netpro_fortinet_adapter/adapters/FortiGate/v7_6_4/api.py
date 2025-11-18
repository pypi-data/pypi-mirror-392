import sys
import json
import requests

from netpro.utils.exceptions import APIError
from netpro.adapters.registry import register_adapter
from ..v7_6 import FORTIGATE as FORTIGATEv76

__all__ = (
    'FORTIGATE',
)

@register_adapter(vendor="fortinet", os="FortiOS", version="7.6.4")
class FORTIGATE(FORTIGATEv76):
    """
    FortiGate Adapter for FortiOS v7.6.4
    """
    
    def _build_login_url(self, ip=None):
        return f"https://{ip or self.ip}:{self.port}/api/v2/authentication"

    def _build_login_payload(self):
        return json.dumps({
            "username": self.user,
            "password": self.password
        })
    
    def _build_logout_url(self) -> str:
        """
        Construct the logout URL. Subclasses should override if vendor uses a different endpoint.
        """
        return f"https://{self.ip}:{self.port}/api/v2/authentication"
    
    def logout(self):
        output = [False, 'Unknown']
        try:
            if not self.session:
                raise APIError('No existing session found.')

            self.logger.info('Logging out...')
            url = self._build_logout_url()
            response = self.session.delete(url, verify=False, timeout=10)

            # Let raise_for_status() catch 4xx/5xx
            response.raise_for_status()

            try:
                output = [True, response.json()]
            except json.JSONDecodeError:
                output = [True, response.text or "Logout successful"]

        except requests.exceptions.Timeout as err:
            self.logger.error(f"Timeout error during logout: {err}")
            output = [False, "Timeout: The device did not respond in time."]

        except requests.exceptions.ConnectionError as err:
            self.logger.error(f"Connection error during logout: {err}")
            output = [False, "Connection Error: Could not reach the device."]

        except requests.exceptions.HTTPError as err:
            status = err.response.status_code
            text = err.response.text.strip()
            self.logger.error(f"HTTP error {status}: {text}")
            output = [False, f"HTTP Error {status}: {text or 'No response body'}"]

        except requests.exceptions.RequestException as err:
            self.logger.error(f"Unexpected request error during logout: {err}")
            output = [False, f"Unexpected error: {err}"]

        except APIError as err:
            self.logger.error(f"API logout error: {err}")
            output = [False, str(err)]

        except Exception:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            msg = f"Unhandled exception during logout: [{exc_traceback.tb_frame.f_code.co_name}:{exc_traceback.tb_lineno}]: {exc_type.__name__}({exc_value})"
            self.logger.exception(msg)
            output = [False, msg]

        finally:
            if self.session:
                self.session.close()
                self.session = None
            return output

