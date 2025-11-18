"""Unit tests for the Clinkey password generator core logic."""

import re
import pytest
from clinkey_cli.main import Clinkey, MAX_PASSWORD_LENGTH, MAX_BATCH_SIZE, MIN_PASSWORD_LENGTH


class TestClinkeyInit:
    """Test Clinkey class initialization."""

    def test_clinkey_instance_creation(self):
        """Test that Clinkey instance is created successfully."""
        clinkey = Clinkey()
        assert clinkey is not None
        assert hasattr(clinkey, '_simple_syllables')
        assert hasattr(clinkey, '_complex_syllables')
        assert hasattr(clinkey, '_separators')

    def test_syllables_not_empty(self, clinkey):
        """Test that syllable lists are populated."""
        assert len(clinkey._simple_syllables) > 0
        assert len(clinkey._complex_syllables) > 0

    def test_default_separators(self, clinkey):
        """Test that default separators are set correctly."""
        assert '-' in clinkey._separators
        assert '_' in clinkey._separators


class TestPasswordGeneration:
    """Test password generation methods."""

    def test_generate_password_default(self, clinkey):
        """Test password generation with default parameters."""
        password = clinkey.generate_password()
        assert isinstance(password, str)
        assert len(password) == 16

    @pytest.mark.parametrize("length,expected", [
        (10, 10),
        (16, 16),
        (20, 20),
        (50, 50),
    ])
    def test_generate_password_length(self, clinkey, length, expected):
        """Test password matches requested length."""
        password = clinkey.generate_password(length=length)
        assert len(password) == expected

    @pytest.mark.parametrize("password_type", ["normal", "strong", "super_strong"])
    def test_generate_password_types(self, clinkey, password_type):
        """Test all password type presets."""
        password = clinkey.generate_password(type=password_type)
        assert isinstance(password, str)
        assert len(password) == 16

    def test_generate_password_lowercase(self, clinkey):
        """Test password lowercase conversion."""
        password = clinkey.generate_password(lower=True)
        assert password.islower() or not password.isalpha()

    def test_generate_password_no_separator(self, clinkey):
        """Test password without separators."""
        password = clinkey.generate_password(no_separator=True)
        assert '-' not in password
        assert '_' not in password

    def test_generate_password_custom_separator(self, clinkey):
        """Test password with custom separator."""
        password = clinkey.generate_password(new_separator='@')
        # Password should contain the custom separator
        assert '@' in password or len(password) < 16

    def test_normal_password_pattern(self, clinkey):
        """Test normal password contains expected characters."""
        password = clinkey.generate_password(type="normal", length=30)
        # Normal passwords should only contain uppercase letters and separators
        assert re.match(r'^[A-Z\-_]+$', password)

    def test_strong_password_pattern(self, clinkey):
        """Test strong password contains letters and digits."""
        password = clinkey.generate_password(type="strong", length=30)
        # Strong passwords should contain letters, digits, and separators
        assert re.match(r'^[A-Z0-9\-_]+$', password)
        assert any(c.isdigit() for c in password)

    def test_super_strong_password_pattern(self, clinkey):
        """Test super strong password contains all character types."""
        password = clinkey.generate_password(type="super_strong", length=40)
        # Should contain letters
        assert any(c.isalpha() for c in password)
        # Should contain digits
        assert any(c.isdigit() for c in password)


class TestInputValidation:
    """Test input validation and error handling."""

    def test_invalid_length_negative(self, clinkey):
        """Test that negative length raises ValueError."""
        with pytest.raises(ValueError, match="length must be at least"):
            clinkey.generate_password(length=-1)

    def test_invalid_length_zero(self, clinkey):
        """Test that zero length raises ValueError."""
        with pytest.raises(ValueError, match="length must be at least"):
            clinkey.generate_password(length=0)

    def test_invalid_length_too_large(self, clinkey):
        """Test that excessive length raises ValueError."""
        with pytest.raises(ValueError, match="cannot exceed"):
            clinkey.generate_password(length=MAX_PASSWORD_LENGTH + 1)

    def test_invalid_type(self, clinkey):
        """Test that invalid password type raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported type"):
            clinkey.generate_password(type="invalid_type")

    def test_invalid_separator_length(self, clinkey):
        """Test that multi-character separator raises ValueError."""
        with pytest.raises(ValueError, match="exactly one character"):
            clinkey.generate_password(new_separator="@@")

    def test_invalid_separator_empty(self, clinkey):
        """Test that empty separator raises ValueError."""
        with pytest.raises(ValueError, match="exactly one character"):
            clinkey.generate_password(new_separator="")

    def test_invalid_separator_whitespace(self, clinkey):
        """Test that whitespace separator raises ValueError."""
        with pytest.raises(ValueError, match="safe printable character"):
            clinkey.generate_password(new_separator=" ")


class TestBatchGeneration:
    """Test batch password generation."""

    def test_generate_batch_default(self, clinkey):
        """Test batch generation with default parameters."""
        passwords = clinkey.generate_batch(count=5)
        assert isinstance(passwords, list)
        assert len(passwords) == 5
        assert all(isinstance(p, str) for p in passwords)

    def test_generate_batch_uniqueness(self, clinkey):
        """Test that batch passwords are sufficiently unique."""
        passwords = clinkey.generate_batch(count=100)
        unique_passwords = set(passwords)
        # Expect high uniqueness (at least 95%)
        assert len(unique_passwords) >= 95

    @pytest.mark.parametrize("count", [1, 5, 10, 50])
    def test_generate_batch_count(self, clinkey, count):
        """Test batch generation produces correct count."""
        passwords = clinkey.generate_batch(count=count)
        assert len(passwords) == count

    def test_generate_batch_invalid_count_zero(self, clinkey):
        """Test that zero count raises ValueError."""
        with pytest.raises(ValueError, match="count must be a positive integer"):
            clinkey.generate_batch(count=0)

    def test_generate_batch_invalid_count_negative(self, clinkey):
        """Test that negative count raises ValueError."""
        with pytest.raises(ValueError, match="count must be a positive integer"):
            clinkey.generate_batch(count=-5)

    def test_generate_batch_too_large(self, clinkey):
        """Test that excessive batch size raises ValueError."""
        with pytest.raises(ValueError, match="cannot exceed"):
            clinkey.generate_batch(count=MAX_BATCH_SIZE + 1)


class TestSeparatorBehavior:
    """Test separator handling and edge cases."""

    def test_custom_separator_state_isolation(self, clinkey):
        """Test that custom separator doesn't leak between calls."""
        # Generate with custom separator
        password1 = clinkey.generate_password(new_separator='@', length=20)
        # Generate without custom separator
        password2 = clinkey.generate_password(length=20)
        # Second password should use default separators
        assert '@' not in password2 or len(password2) < 5

    def test_no_separator_removes_all(self, clinkey):
        """Test that no_separator removes default separators."""
        password = clinkey.generate_password(no_separator=True, length=30)
        assert '-' not in password
        assert '_' not in password

    def test_custom_separator_with_no_separator(self, clinkey):
        """Test custom separator with no_separator flag."""
        password = clinkey.generate_password(
            new_separator='@',
            no_separator=True,
            length=20
        )
        assert '@' not in password


class TestPasswordQuality:
    """Test password quality and randomness properties."""

    def test_password_randomness(self, clinkey):
        """Test that consecutive passwords are different."""
        passwords = [clinkey.generate_password() for _ in range(20)]
        unique = set(passwords)
        # All should be unique
        assert len(unique) == 20

    def test_password_no_empty_strings(self, clinkey):
        """Test that generated passwords are never empty."""
        for _ in range(50):
            password = clinkey.generate_password(length=10)
            assert len(password) > 0

    def test_minimum_length_password(self, clinkey):
        """Test password generation at minimum length."""
        password = clinkey.generate_password(length=MIN_PASSWORD_LENGTH)
        assert len(password) == MIN_PASSWORD_LENGTH

    def test_large_password_generation(self, clinkey):
        """Test generation of very large passwords."""
        password = clinkey.generate_password(length=1000)
        assert len(password) == 1000
