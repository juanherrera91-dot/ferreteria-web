from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

hash_password = bcrypt.generate_password_hash("admin123").decode('utf-8')

print(hash_password)