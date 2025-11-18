import json
import importlib.resources
from datetime import datetime
import pytz

class EncryptionError(Exception):
    pass

class DecryptionError(Exception):
    pass

class NE:
    def __init__(self):
        self.code_maps = self.load_maps()
        self.prefix_to_minute = {v["C"]: k for k, v in self.code_maps.items()}
    
    def load_maps(self) -> dict:
        with importlib.resources.open_text(__package__, 'map.json', encoding='utf-8') as f:
            return json.load(f)

    def validate_number(self, number_str: str):
        if not number_str.isdigit():
            raise EncryptionError("Number must contain digits only.")
    
    def validate_code(self, code_str: str):
        if len(code_str) < 2:
            raise DecryptionError("Code is too short.")
        prefix = code_str[:2]
        if prefix not in self.prefix_to_minute:
            raise DecryptionError("Code prefix is unknown.")
        code_body = code_str[2:]
        if len(code_body) % 3 != 0:
            raise DecryptionError("Invalid code length.")

    def encrypt_number(self, number_str: str, minute_key: int) -> str:
        self.validate_number(number_str)
        minute_str = f"{minute_key:02d}"
        code_map = self.code_maps.get(minute_str)
        if not code_map:
            raise EncryptionError(f"No encryption map for minute {minute_str}")
        
        prefix = code_map["C"]
        codes = code_map["codes"]
        
        encrypted_parts = []
        for digit in number_str:
            code = codes.get(digit)
            if code is None:
                raise EncryptionError(f"Digit '{digit}' not found in encryption map.")
            encrypted_parts.append(code)
        
        return prefix + "".join(encrypted_parts)

    def EN(self, number_str: str) -> str:
        tz = pytz.timezone("Africa/Cairo")
        now = datetime.now(tz)
        return self.encrypt_number(number_str, now.minute)

    def split_codes(self, code_str: str, prefixes: set) -> list[str]:
        parts = []
        i = 0
        while i < len(code_str):
            if i + 2 > len(code_str):
                raise DecryptionError(f"Incomplete prefix at position {i}.")
            prefix = code_str[i:i+2]
            if prefix not in prefixes:
                raise DecryptionError(f"Unknown prefix '{prefix}' at position {i}.")
            j = i + 2
            while j < len(code_str):
                if j + 2 <= len(code_str) and code_str[j:j+2] in prefixes:
                    break
                j += 3
            parts.append(code_str[i:j])
            i = j
        return parts

    def DN(self, code_str: str) -> str:
        prefixes = set(self.prefix_to_minute.keys())
        codes_parts = self.split_codes(code_str, prefixes)
        decrypted_full = []
        for part in codes_parts:
            self.validate_code(part)
            prefix = part[:2]
            minute_key = self.prefix_to_minute[prefix]
            code_map = self.code_maps[minute_key]
            codes = code_map["codes"]
            code_to_number = {v: k for k, v in codes.items()}

            code_body = part[2:]
            chunk_size = 3
            decrypted_parts = []
            for i in range(0, len(code_body), chunk_size):
                chunk = code_body[i:i+chunk_size]
                digit = code_to_number.get(chunk)
                if digit is None:
                    raise DecryptionError(f"Code chunk '{chunk}' is invalid.")
                decrypted_parts.append(digit)
            decrypted_full.append("".join(decrypted_parts))
        return "".join(decrypted_full)
