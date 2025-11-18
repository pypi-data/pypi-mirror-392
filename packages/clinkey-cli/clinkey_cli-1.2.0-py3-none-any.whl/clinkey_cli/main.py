"""
Core password generation logic for the Clinkey CLI package.

Exposes the :class:`Clinkey` password generator and a module-level ``clinkey``
instance used by the CLI entrypoints.
"""

import secrets
import string
from typing import Callable, Dict

# Security and validation constants
MAX_PASSWORD_LENGTH = 128
MAX_BATCH_SIZE = 500
MIN_PASSWORD_LENGTH = 16

# Safe separator characters (printable, non-whitespace)
SAFE_SEPARATOR_CHARS = string.printable.replace(' \t\n\r\x0b\x0c', '')


class Clinkey:
    """Generate pronounceable passwords with configurable complexity levels.

    Attributes
    ----------
    _consonants : list[str]
        Consonants from the Latin alphabet used to compose syllables.
    _vowels : list[str]
        Vowels from the Latin alphabet paired with consonants.
    _digits : list[str]
        Digits from ``0`` through ``9`` used in numeric blocks.
    _specials : list[str]
        Safe special characters allowed in generated passwords.
    _simple_syllables : list[str]
        Consonant/vowel pairs used to build pronounceable chunks.
    _complex_syllables : list[str]
        Predefined consonant clusters approximating French phonetics.
    _separators : list[str]
        Default separators inserted between generated chunks.
    _generators : dict[str, Callable[[], str]]
        Mapping of password type name to the generator method.
    new_separator : str | None
        Custom separator overriding the default ones when provided.

    Methods
    -------
    normal()
        Generate a pronounceable password made of words and separators.
    strong()
        Generate a password made of words, digits, and separators.
    super_strong()
        Generate a password that also includes special characters.
    generate_password(...)
        Produce a single password with optional casing and separator tweaks.
    generate_batch(...)
        Produce several passwords as a convenience helper.
    """

    def __init__(self) -> None:
        alphabet = string.ascii_uppercase
        vowels = "AEIOUY"
        self._consonants = [char for char in alphabet if char not in vowels]
        self._vowels = list(vowels)
        self._digits = list(string.digits)
        self._specials = [
            char
            for char in string.punctuation
            if char not in {"-", "_", "$", "#", "|", "<", ">", "(", ")", "[", "]", "{", "}", '"', "'", "`", "@", " "}
        ]

        self._simple_syllables = [consonant + vowel for consonant in self._consonants for vowel in self._vowels]
        self._complex_syllables = [
            "TRE",
            "TRI",
            "TRO",
            "TRA",
            "TRU",
            "TRY",
            "TSA",
            "TSE",
            "TSI",
            "TSO",
            "TSU",
            "TSY",
            "DRE",
            "DRI",
            "DRO",
            "DRA",
            "DRU",
            "DRY",
            "BRE",
            "BRI",
            "BRO",
            "BRA",
            "BRU",
            "BRY",
            "BLA",
            "BLE",
            "BLI",
            "BLO",
            "BLU",
            "BLY",
            "CRE",
            "CRI",
            "CRO",
            "CRA",
            "CRU",
            "CRY",
            "CHA",
            "CHE",
            "CHI",
            "CHO",
            "CHU",
            "CHY",
            "FRE",
            "FRI",
            "FRO",
            "FRA",
            "FRY",
            "FLA",
            "FLE",
            "FLI",
            "FLO",
            "FLU",
            "FLY",
            "GRE",
            "GRI",
            "GRO",
            "GRA",
            "GRU",
            "GRY",
            "GLA",
            "GLE",
            "GLI",
            "GLO",
            "GLU",
            "GLY",
            "GNA",
            "GNE",
            "GNI",
            "GNO",
            "GNU",
            "GNY",
            "PRE",
            "PRI",
            "PRO",
            "PRA",
            "PRU",
            "PRY",
            "PLA",
            "PLE",
            "PLI",
            "PLO",
            "PLU",
            "PLY",
            "QUA",
            "QUE",
            "QUI",
            "QUO",
            "QUY",
            "SRE",
            "SRI",
            "SRO",
            "SRA",
            "SRU",
            "SRY",
            "SLA",
            "SLE",
            "SLI",
            "SLO",
            "SLU",
            "SLY",
            "STA",
            "STE",
            "STI",
            "STO",
            "STU",
            "STY",
            "SNA",
            "SNE",
            "SNI",
            "SNO",
            "SNU",
            "SNY",
            "SMA",
            "SME",
            "SMI",
            "SMO",
            "SMU",
            "SMY",
            "SHA",
            "SHE",
            "SHI",
            "SHO",
            "SHU",
            "SHY",
            "SPY",
            "SPA",
            "SPE",
            "SPI",
            "SPO",
            "SPU",
            "VRE",
            "VRI",
            "VRO",
            "VRA",
            "VRU",
            "VRY",
            "VLA",
            "VLE",
            "VLI",
            "VLO",
            "VLU",
            "VLY",
            "VNA",
            "VNE",
            "VNI",
            "VNO",
            "VNU",
            "VNY",
            "VHA",
            "VHE",
            "VHI",
            "VHO",
            "VHU",
            "VHY",
            "VJA",
            "VJE",
            "VJI",
            "VJO",
            "VJU",
            "VJY",
            "WHA",
            "WHE",
            "WHI",
            "WHO",
            "WHU",
            "ZRE",
            "ZRU",
            "ZRI",
            "ZRO",
            "ZRA"
        ]

        self._separators = ["-", "_"]
        self._generators: Dict[str, Callable[[], str]] = {
            "normal": self.normal,
            "strong": self.strong,
            "super_strong": self.super_strong,
        }
        # Custom separator to override the default ones ('-' and '_') when set
        self.new_separator = None

    def _generate_simple_syllable(self) -> str:
        """Return a two-letter syllable built from a consonant and a vowel."""
        return secrets.choice(self._simple_syllables)

    def _generate_complex_syllable(self) -> str:
        """Return a three-letter syllable approximating French pronunciation."""
        return secrets.choice(self._complex_syllables)

    def _generate_pronounceable_word(self, min_length: int = 4, max_length: int = 10) -> str:
        """Compose a pronounceable pseudo-word from the predefined syllables.

        Parameters
        ----------
        min_length : int, default 4
            Minimum length of the generated word.
        max_length : int, default 10
            Maximum length of the generated word.

        Returns
        -------
        str
            Pseudo-word trimmed to stay within the specified bounds.
        """
        word = self._generate_simple_syllable()
        target = secrets.randbelow(max_length - min_length + 1) + min_length

        while len(word) < target:
            generator = secrets.choice([self._generate_simple_syllable, self._generate_complex_syllable])
            word += generator()

        return word[:target]

    def _generate_number_block(self, length: int = 3) -> str:
        """Return a numeric block composed exclusively of digits."""
        return "".join(secrets.choice(self._digits) for _ in range(length))

    def _generate_special_characters_block(self, length: int = 3) -> str:
        """Return a block made of randomly selected special characters."""
        return "".join(secrets.choice(self._specials) for _ in range(length))

    def _generate_separator(self) -> str:
        """Return the separator to use between password segments."""
        if self.new_separator:
            return self.new_separator
        return secrets.choice(self._separators)

    def super_strong(self) -> str:
        """
        Generate a password mixing words, digits, special chars, and separators.

        Returns
        -------
        str
            Password combining three pronounceable words with numeric and
            special-character blocks.
        """
        words = [self._generate_pronounceable_word(secrets.randbelow(3) + 4, secrets.randbelow(5) + 8) for _ in range(3)]
        numbers = [self._generate_number_block(secrets.randbelow(4) + 3) for _ in range(3)]
        specials = [self._generate_special_characters_block(secrets.randbelow(4) + 3) for _ in range(2)]
        separators = [self._generate_separator() for _ in range(6)]

        result = []
        result.append(words.pop() + separators.pop() + specials.pop() + separators.pop() + numbers.pop() + separators.pop())
        result.append(words.pop() + separators.pop() + specials.pop() + separators.pop() + numbers.pop() + separators.pop())
        result.append(words.pop())
        return "".join(result)

    def strong(self) -> str:
        """Generate a password built from pronounceable words and digit blocks.

        Returns
        -------
        str
            Password interleaving words and numeric blocks separated by
            the configured delimiters.
        """
        words = [self._generate_pronounceable_word(secrets.randbelow(3) + 4, secrets.randbelow(5) + 8) for _ in range(3)]
        numbers = [self._generate_number_block(secrets.randbelow(4) + 3) for _ in range(3)]
        separators = [self._generate_separator() for _ in range(6)]

        result = []
        for _ in range(3):
            result.append(words.pop(0) + separators.pop(0) + numbers.pop(0) + separators.pop(0))
        return "".join(result)

    def normal(self) -> str:
        """Generate a pronounceable password made solely of uppercase letters."""
        words = [self._generate_pronounceable_word(secrets.randbelow(3) + 4, secrets.randbelow(5) + 8) for _ in range(3)]
        separators = [self._generate_separator() for _ in range(6)]

        result = []
        for _ in range(3):
            result.append(words.pop(0) + separators.pop(0))
        return "".join(result)

    def _fit_to_length(self, generator: Callable[[], str], target_length: int) -> str:
        """Compose a password until the requested length is exactly reached.

        Parameters
        ----------
        generator : Callable[[], str]
            Function that yields password chunks (e.g. ``self.normal``).
        target_length : int
            Desired length for the final password.

        Returns
        -------
        str
            Generated password whose length exactly matches ``target_length``.
        """
        password = ""
        while len(password) < target_length:
            chunk = generator()
            if len(password) + len(chunk) <= target_length:
                password += chunk
            else:
                remaining = target_length - len(password)
                password += chunk[:remaining]
                break
        return password

    def generate_password(
        self,
        length: int = 16,
        type: str = "normal",
        lower: bool = False,
        no_separator: bool = False,
		new_separator: str | None = None,
		output: str | None = None
    ) -> str:
        """
        Generate a single password matching the requested configuration.

        Parameters
        ----------
        length : int, default 16
            Length of the password to produce.
        type : str, default "normal"
            Password preset to use. Supported values are ``"normal"``,
            ``"strong"``, and ``"super_strong"``.
        lower : bool, default False
            When ``True``, convert the generated password to lowercase.
        no_separator : bool, default False
            When ``True``, remove all separator characters from the result.
        new_separator : str | None, default None
            Optional custom separator applied for this generation only.
        output : str | None, default None
            Optional output path consumed by the CLI layer; no file I/O is
            performed inside this method.

        Returns
        -------
        str
            Password assembled according to the provided arguments.

        Raises
        ------
        ValueError
            If ``length`` is not strictly positive or ``type`` is unknown.
        """
        if length < MIN_PASSWORD_LENGTH:
            raise ValueError(f"length must be at least {MIN_PASSWORD_LENGTH}")
        if length > MAX_PASSWORD_LENGTH:
            raise ValueError(f"length cannot exceed {MAX_PASSWORD_LENGTH}")

        # Validate separator if provided
        if new_separator is not None:
            if len(new_separator) != 1:
                raise ValueError("separator must be exactly one character")
            if new_separator not in SAFE_SEPARATOR_CHARS:
                raise ValueError("separator must be a safe printable character (no whitespace)")

        key = type.strip().lower()
        if key not in self._generators:
            valid = ", ".join(sorted(self._generators.keys()))
            raise ValueError(f"Unsupported type '{type}'. Choose among: {valid}.")

        # Temporarily override separator for this generation if provided
        previous_separator = self.new_separator
        if new_separator is not None:
            self.new_separator = new_separator

        try:
            raw_password = self._fit_to_length(self._generators[key], length)
        finally:
            # Restore previous separator to avoid leaking state between calls
            self.new_separator = previous_separator

        separators_to_strip = "-_"
        effective_separator = new_separator if new_separator is not None else previous_separator
        if effective_separator and effective_separator not in "-_":
            separators_to_strip += effective_separator

        cleaned = raw_password.strip(separators_to_strip)

        if no_separator:
            cleaned = cleaned.replace("-", "").replace("_", "")
            if effective_separator and effective_separator not in "-_":
                cleaned = cleaned.replace(effective_separator, "")

        if lower:
            cleaned = cleaned.lower()

        return cleaned

    def generate_batch(
        self,
        length: int = 16,
        type: str = "normal",
        count: int = 1,
        lower: bool = False,
        no_separator: bool = False,
		new_separator: str | None = None,
		output: str | None = None
    ) -> list[str]:
        """Generate several passwords reusing ``generate_password`` defaults.

        Parameters
        ----------
        length : int, default 16
            Length of each password to produce.
        type : str, default "normal"
            Password preset to use for every generated password.
        count : int, default 1
            Number of passwords to return.
        lower : bool, default False
            When ``True``, return passwords in lowercase.
        no_separator : bool, default False
            When ``True``, strip separators from each password.
        new_separator : str | None, default None
            Separator override to propagate to each generation.
        output : str | None, default None
            Optional output path retained for interface parity with the CLI.

        Returns
        -------
        list[str]
            List of passwords generated with the provided arguments.

        Raises
        ------
        ValueError
            If ``count`` is not strictly positive.
        """
        if count <= 0:
            raise ValueError("count must be a positive integer")
        if count > MAX_BATCH_SIZE:
            raise ValueError(f"count cannot exceed {MAX_BATCH_SIZE}")

        return [
            self.generate_password(
                length=length,
                type=type,
                lower=lower,
                no_separator=no_separator,
                new_separator=new_separator,
            )
            for _ in range(count)
        ]


clinkey = Clinkey()

__all__ = ["Clinkey", "clinkey"]
