from database import db

class PasswordModel:
    def __init__(self, length, include_numbers, include_special_characters):
        self.length = length
        self.include_numbers = include_numbers
        self.include_special_characters = include_special_characters

    def generate_password(self):
        import secrets
        import string

        characters = string.ascii_letters
        if self.include_numbers:
            characters += string.digits
        if self.include_special_characters:
            characters += string.punctuation

        password = ''.join(secrets.choice(characters) for _ in range(self.length))
        return password