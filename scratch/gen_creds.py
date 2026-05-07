import base64

def obfuscate(text, key):
    data = text.encode('utf-8')
    key_bytes = key.encode('utf-8')
    enc = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data))
    return base64.b64encode(enc).decode('utf-8')

key = "VeloraSuperSecureKeyForObfuscation2026!"
project_id = "bb6bd9b3"
api_key = "290b215854301115161615625402561a125e416a5254521012124b4254081757571012124a425408175712"

print(f"PROJECT_ID: {obfuscate(project_id, key)}")
print(f"API_KEY: {obfuscate(api_key, key)}")
