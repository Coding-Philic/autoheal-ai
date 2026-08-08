"""A deliberately buggy Python app for testing AutoHeal."""
import time


def get_user(user_id):
    """Simulate a database lookup that returns None."""
    users = {1: {"name": "Alice"}, 2: {"name": "Bob"}}
    return users.get(user_id)  # Returns None for unknown IDs


def process_user(user_id):
    """Process user — will crash if user doesn't exist."""
    user = get_user(user_id)
    # BUG: No null check — will raise TypeError
    print(f"Processing user: {user['name']}")


if __name__ == "__main__":
    print("Starting app...")
    time.sleep(0.5)
    process_user(1)   # Works fine
    process_user(999) # CRASH: TypeError: 'NoneType' object is not subscriptable
