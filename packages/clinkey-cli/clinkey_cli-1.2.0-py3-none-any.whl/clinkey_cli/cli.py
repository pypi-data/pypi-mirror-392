"""Click-powered command line interface for the Clinkey password generator.

Supports both interactive and scripted launches, pairing Click for argument
parsing with Rich for terminal rendering.
"""
import pathlib
from typing import Iterable, Optional

import click
from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from clinkey_cli.main import Clinkey
from clinkey_cli.logos import animate_logo, display_logo


console = Console(style="on grey11")


class ClinkeyView:
    """Render the interactive experience using Rich panels and prompts.

    Attributes
    ----------
    _logo_style : dict[str, str]
        Color palette applied to the ASCII art logo and panels.

    Methods
    -------
    display_logo()
        Show the full-screen welcome screen before collecting input.
    ask_for_type()
        Request the desired password profile from the user.
    ask_for_length()
        Request the target password length.
    ask_for_number()
        Request how many passwords should be generated.
    ask_for_options()
        Collect additional option toggles.
    ask_for_output_path()
        Ask where the results should be written.
    ask_for_separator()
        Request a custom separator to override the defaults.
    display_passwords(...)
        Render generated passwords in a styled table.
    """

    def __init__(self) -> None:
        self._logo_style = {
            "title_color": "bold light_green",
            "accent_color": "orchid1",
            "text_color": "grey100",
        }

    def _clear(self) -> None:
        """Clear the console before rendering the next view."""
        console.clear()

    def _logo_panel(self) -> Panel:
        """Build the Rich panel containing the Clinkey ASCII logo.

        Returns
        -------
        rich.panel.Panel
            Panel instance ready to be rendered by the console.
        """
        logo = Text(
            r"""
              |   |              |     \        |    |      /     _____|     \        /
         _____|   |      __    __|      \       |    |     /     |            \      /
        |         |           |          \      |    |    /      |             \    /
        |         |           |       |   \     |        /        __|              /
        |         |           |       |    \    |        \       |                |
        |         |           |       |         |    |    \      |                |
              |        |         |    |         |    |     \           |          |
       _______| _______| ________| ___|     ____| ___|   ___\  ________|      ____|       
             """,
            style=self._logo_style["title_color"],
        )
        return Panel.fit(
            logo,
            padding=(0, 2),
            box=box.ROUNDED,
            border_style=self._logo_style["accent_color"],
        )

    def fullscreen_logo(self):
        animate_logo(fullscreen=True)
        display_logo(fullscreen=True)

    def simple_logo(self):
        animate_logo()
        display_logo()

    def display_logo(self) -> None:
        """Display the full-screen welcome screen and pause until the user confirms.

        The welcome screen fills the terminal with a large ASCII art logo,
        decorative elements, and branding. It is vertically centered based on
        the terminal height.
        """
        self._clear()
        # Get terminal height to create proper vertical centering
        terminal_height = console.size.height
        # Add some top padding for better vertical centering
        top_padding = max(0, (terminal_height // 2))
        console.print("\n" * top_padding)
        # Display the full-screen logo layout
        if terminal_height >= 50:
            self.fullscreen_logo()
        else:
            self.simple_logo()

        # Wait for user input (cursor will be at the end of the layout)
        input()
    
    def intro_logo(self) -> None:
        """Display the intro logo animation."""
        self._clear()
        animate_logo()
        display_logo()
        input()

    def ask_for_type(self) -> str:
        """Prompt the user for a password profile and return its slug.

        Returns
        -------
        str
            Password preset identifier (``"normal"``, ``"strong"``, or
            ``"super_strong"``); defaults to ``"normal"`` when the input
            is unrecognised.
        """
        self._clear()
        console.print(Align.center(self._logo_panel()))
        console.print(
            Align.center(
                Text.from_markup(
                    "How [bold light_green]BOLD[/] do you want your password?\n",
                    style="white",
                )
            )
        )
        choices = Text.from_markup(
            "1 - [bold orchid1]Vanilla[/] (letters only)\n"
            "2 - [bold orchid1]Twisted[/] (letters and digits)\n"
            "3 - [bold orchid1]So NAAASTY[/] (letters, digits, symbols)",
            style="white",
        )
        console.print(Align.center(choices))
        console.print(
            Align.center(
                Text.from_markup(
                    "Choose your [bold light_green]TRIBE[/] (1 / 2 / 3): ",
                    style="bright_black",
                )
            ),
            end="",
        )
        choice = input().strip()
        return {"1": "normal", "2": "strong", "3": "super_strong"}.get(choice, "normal")

    def ask_for_length(self) -> int:
        """Prompt for the target password length, falling back to ``16``.

        Returns
        -------
        int
            Positive length chosen by the user; returns ``16`` when the
            provided value is empty, invalid, or non-positive.
        """
        self._clear()
        console.print(Align.center(self._logo_panel()))
        console.print(
            Align.center(
                Text.from_markup(
                    "How [bold light_green]LONG[/] do you like it ?",
                    style="white",
                )
            )
        )
        console.print(
            Align.center(Text.from_markup("(default: 16): ", style="bright_black")),
            end="",
        )
        value = input().strip()
        try:
            length = int(value)
            return length if length > 0 else 16
        except ValueError:
            return 16

    def ask_for_number(self) -> int:
        """Prompt for the number of passwords to generate, defaulting to ``1``.

        Returns
        -------
        int
            Positive count requested by the user; returns ``1`` when the
            provided value is empty, invalid, or non-positive.
        """
        self._clear()
        console.print(Align.center(self._logo_panel()))
        console.print(
            Align.center(
                Text.from_markup(
                    "How [bold light_green]MANY[/] you fancy at once ?",
                    style="white",
                )
            )
        )
        console.print(
            Align.center(Text.from_markup("(default: 1): ", style="bright_black")),
            end="",
        )
        value = input().strip()
        try:
            count = int(value)
            return count if count > 0 else 1
        except ValueError:
            return 1

    def ask_for_options(self) -> list[str]:
        """Prompt for extra option keywords such as ``lower`` or ``no_sep``.

        Returns
        -------
        list[str]
            Tokens entered by the user separated by whitespace; returns an
            empty list when no extra options are provided.
        """
        self._clear()
        console.print(Align.center(self._logo_panel()))
        console.print(
            Align.center(
                Text.from_markup(
                    "Any extra [bold light_green]OPTIONS[/]? (separate by spaces)",
                    style="white",
                )
            )
        )
        console.print(
            Align.center(Text.from_markup(
                "Available: lower, no_sep", 
                style="bright_black"
                )
                )
        )
        choices = input().strip()
        return choices.split() if choices else []

    def ask_for_output_path(self) -> Optional[str]:
        """Prompt for an output file path, returning ``None`` when skipped.

        Returns
        -------
        str | NoneUns§ fè
            Absolute or relative path entered by the user, or ``None`` if the
            prompt is left blank.
        """
        self._clear()
        console.print(Align.center(self._logo_panel()))
        console.print(
            Align.center(
                Text.from_markup(
                    "Enter a file path to save the result (press ENTER to skip):",
                    style="white",
                )
            ),
            end="",
        )
        value = input().strip()
        return value or None

    def ask_for_separator(self) -> Optional[str]:
        """Prompt for a custom separator character, returning its first char.

        Returns
        -------
        str | None
            First character of the user input when provided; otherwise ``None``.
        """
        self._clear()
        console.print(Align.center(self._logo_panel()))
        console.print(
            Align.center(
                Text.from_markup(
                    "Custom [bold light_green]SEPARATOR[/]? (press ENTER to skip)",
                    style="white",
                )
            )
        )
        console.print(
            Align.center(
                Text.from_markup("Use exactly one non-space character.", style="bright_black")
            )
        )
        console.print(
            Align.center(Text.from_markup("Value: ", style="bright_black")),
            end="",
        )
        value = input().strip()
        if not value:
            return None
        return value[0]

    def display_passwords(self, passwords: Iterable[str]) -> None:
        """Render generated passwords in a Rich table for easy copying.

        Parameters
        ----------
        passwords : Iterable[str]
            Collection of passwords to render.
        """
        self._clear()
        console.print(Align.center(self._logo_panel()))
        console.print(
            Align.center(
                Panel.fit(
                    Align.center(
                        Text.from_markup((
                            "Your Clinkey [bold light_green]PASSWORDS[/] "
                            "are [bold light_green]READY[/]"
                            ),
                            style="white"
                        )
                    ),
                    padding=(0, 1),
                    box=box.ROUNDED,
                    border_style=self._logo_style["accent_color"],
                )
            )
        )
        table = Table(show_header=False, box=box.ROUNDED, border_style=self._logo_style["accent_color"])
        table.add_column("password", style=self._logo_style["title_color"], justify="center")
        for password in passwords:
            table.add_row(Text(password, style="bold light_green", justify="center"))
        console.print(Align.center(table))

        console.print(
            Align.center(
                Text.from_markup("Choose one to copy !", style="white"),
            )
        )


view = ClinkeyView()

def _parse_extra_options(options: Iterable[str]) -> dict[str, bool]:
    """Map option tokens collected interactively to CLI flag booleans.

    Parameters
    ----------
    options : Iterable[str]
        Raw tokens provided by the user.

    Returns
    -------
    dict[str, bool]
        Dictionary with ``lower`` and ``no_sep`` keys indicating whether each
        option has been requested. Unrecognised tokens are ignored.
    """
    lookup = {
        "lower": {"lower", "low", "-l", "--lower", "lw"},
        "no_sep": {"no_sep", "nosep", "-ns", "--no-sep", "no-sep", "ns"},
    }
    result = {"lower": False, "no_sep": False}
    for option in options:
        token = option.strip().lower()
        for key, aliases in lookup.items():
            if token in aliases:
                result[key] = True
    return result


def _write_passwords(path: pathlib.Path, passwords: Iterable[str]) -> None:
    """Persist generated passwords to the provided file path.

    Parameters
    ----------
    path : pathlib.Path
        Destination file that will receive the passwords.
    passwords : Iterable[str]
        Passwords to write, one per line. The iterable is consumed once.
    """
    with path.open("w", encoding="utf-8") as handle:
        for password in passwords:
            handle.write(f"{password}\n")


@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("-l", 
              "--length", 
              type=int, 
              default=None, 
              help="Password length (default: 16).")
@click.option("-t",
              "--type",
              "type_",
              type=click.Choice(["normal", "strong", "super_strong"], 
                                 case_sensitive=False),
              default=None,
              help="Password profile: normal, strong, or super_strong.")
@click.option("-n",
              "--number",
              type=int,
              default=None,
              help="Number of passwords to generate (default: 1).",)
@click.option("-ns", 
              "--no-sep", 
              "no_sep", 
              is_flag=True, 
              help="Remove separators from the result.")
@click.option("-low", 
              "--lower", 
              is_flag=True, 
              help="Convert generated passwords to lowercase.")
@click.option("-s",
              "--separator",
              "new_separator",
              type=str,
              default=None,
              help="Use a custom separator character instead of '-' and '_'.")
@click.option("-o",
              "--output",
              type=click.Path(dir_okay=False, 
                              writable=True, 
                              resolve_path=True, 
                              path_type=pathlib.Path),
              default=None,
              help="Write the result to a file instead of displaying it.")
def main(length: Optional[int],
         type_: Optional[str],
         number: Optional[int],
         no_sep: bool,
         lower: bool,
         new_separator: Optional[str],
         output: Optional[pathlib.Path]) -> None:
    """Generate secure, pronounceable passwords from the command line.

    Parameters
    ----------
    length : int | None
        Desired password length. When ``None``, prompt the user interactively.
    type_ : str | None
        Password profile to use. Supported values: ``"normal"``, ``"strong"``,
        ``"super_strong"``. When ``None``, prompt the user interactively.
    number : int | None
        Number of passwords to output. Defaults to ``1`` if left ``None``.
    no_sep : bool
        Strip separator characters from each password when ``True``.
    lower : bool
        Convert generated passwords to lowercase when ``True``.
    new_separator : str | None
        Optional custom separator to apply to generated passwords.
    output : pathlib.Path | None
        Path where passwords should be saved. When ``None``, display them to
        stdout or via the interactive view.

    Raises
    ------
    click.BadParameter
        If ``new_separator`` is provided but is not exactly one non-space
        character.
    """

    generator = Clinkey()

    interactive = length is None and type_ is None and number is None

    if interactive:
        view.display_logo()
        length = view.ask_for_length()
        type_ = view.ask_for_type()
        number = view.ask_for_number()
        extra = _parse_extra_options(view.ask_for_options())
        lower = extra["lower"]
        no_sep = extra["no_sep"]
        chosen_sep = view.ask_for_separator()
        if chosen_sep:
            new_separator = chosen_sep
        chosen_output = view.ask_for_output_path()
        if chosen_output:
            output = pathlib.Path(chosen_output).expanduser().resolve()

    length = 16 if not length else length
    type_ = "normal" if not type_ else type_.lower()
    number = 1 if not number else number

    if new_separator:
        new_separator = new_separator.strip()
        if len(new_separator) != 1 or new_separator.isspace():
            raise click.BadParameter(
                "Separator must be exactly one non-space character.", 
                param_hint="--separator"
            )

    passwords = generator.generate_batch(
        length=length,
        type=type_,
        count=number,
        lower=lower,
        no_separator=no_sep,
        new_separator=new_separator,
    )

    if output:
        _write_passwords(output, passwords)
        click.echo(f"Passwords saved to {output}")
    elif interactive:
        view.display_passwords(passwords)
    else:
        for password in passwords:
            click.echo(password)


if __name__ == "__main__":  # pragma: no cover
    main()
