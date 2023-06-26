# Importing Python Libraies
import hashlib
import base64


class Checksum:
    def calculateChecksum(self, data, secretKey):
        checksum = hashlib.md5(data + secretKey).hexdigest()
        return checksum

    def encrypt(self, data, salt):
        key = salt + "@" + data
        encryptedkey = hashlib.sha256(str(key).encode("utf-8")).hexdigest()
        return encryptedkey

    def encryptSha256(self, k):
        key = hashlib.sha256(str(k).encode("utf-8")).hexdigest()
        return key

    def calculateChecksumSha256(self, data, salt):
        key = salt + "@" + data
        checksum = hashlib.sha256(str(key).encode("utf-8")).hexdigest()
        return checksum

    def calculateMerDom(self, data):
        return base64.b64encode(data.encode("utf-8"))

    def outputForm(self, data):
        html = str()
        for key, value in data.items():
            html += '<input type="hidden" name="' + key + '" value="' + value + '" />'
        return html

    def verifyChecksum(self, checksum, all, secret):
        calChecksum = self.calculateChecksum(secret, all)
        bool = 0

        if checksum == calChecksum:
            bool = 1

        return bool
