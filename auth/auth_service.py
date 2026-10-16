from .database import create_user, get_user
from .security import hash_password, verify_password


def register_user(name, email, password):
    name = name.strip()
    email = email.strip().lower()

    if not name or not email or not password:
        return False, "All fields are required."

    role = "customer"

    if len(password) < 6:
        return False, "Password must contain at least 6 characters."

    password_hash = hash_password(password)

    created = create_user(
        name=name,
        email=email,
        password_hash=password_hash,
        role=role,
    )

    if not created:
        return False, "An account with this email already exists."

    return True, "Registration successful."


def login_user(email, password):
    email = email.strip().lower()

    user = get_user(email)

    if user is None:
        return False, "Invalid email or password."

    user_id, name, email, password_hash, role = user

    if not verify_password(password, password_hash):
        return False, "Invalid email or password."

    return True, {
        "id": user_id,
        "name": name,
        "email": email,
        "role": role,
    }
