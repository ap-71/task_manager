from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext


# Установки безопасности
SECRET_KEY = "your_secret_key"  # Измените на более безопасный ключ
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Инициализация шифрования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
