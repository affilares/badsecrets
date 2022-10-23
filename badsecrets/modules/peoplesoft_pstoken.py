import zlib
import base64
import hashlib
from badsecrets.base import BadsecretsBase, generic_base64_regex


class Peoplesoft_PSToken(BadsecretsBase):

    identify_regex = generic_base64_regex

    def __init__(self, PS_TOKEN_B64):
        self.PS_TOKEN = base64.b64decode(PS_TOKEN_B64)

    def check_secret(self):

        SHA1_mac = self.PS_TOKEN[44:64]
        try:
            PS_TOKEN_DATA = zlib.decompress(self.PS_TOKEN[76:])
        except zlib.error:
            return False

        username = PS_TOKEN_DATA[21 : 21 + PS_TOKEN_DATA[20]].replace(b"\x00", b"").decode()

        # try no password
        h = hashlib.sha1(PS_TOKEN_DATA)
        if h.digest() == SHA1_mac:
            self.output_parameters = {"PS_TOKEN_password": "BLANK PASSWORD!", "username": username}
            return True

        for l in self.load_resource("peoplesoft_passwords.txt"):
            password = l.strip()

            h = hashlib.sha1(PS_TOKEN_DATA + password.encode("utf_16_le", errors="ignore"))
            if h.digest() == SHA1_mac:
                self.output_parameters = {"PS_TOKEN_password": password, "username": username}
                return True

        return False
