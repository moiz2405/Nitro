import os
import json


class UserProfileManager:
    def __init__(self, storage_file="user_profile.json"):
        self.storage_file = storage_file
        self.data = self._load_data()

    def _load_data(self) -> dict:
        """Load user data from the storage file."""
        if os.path.exists(self.storage_file):
            try:
                with open(self.storage_file, "r") as file:
                    return json.load(file)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save_data(self) -> None:
        """Save user data to the storage file."""
        with open(self.storage_file, "w") as file:
            json.dump(self.data, file, indent=4)

    def get_preference(self, key: str, default=None):
        """Retrieve a preference by key."""
        return self.data.get(key, default)

    def set_preference(self, key: str, value) -> None:
        """Set or update a preference."""
        self.data[key] = value
        self.save_data()

    def get_all_preferences(self) -> dict:
        """Retrieve all stored preferences."""
        return self.data
