from itsdangerous import URLSafeTimedSerializer
from key import secret_key
def token(data,salt):
    serializer = URLSafeTimedSerializer(seecret_key)
    return serializer.dumps(data = data,salt = salt)