from rich.text import Text
from time import sleep
from rich.console import Console, Group
from rich.align import Align
from rich.panel import Panel
from rich.layout import Layout
from rich import box

from clinkey_cli.const import LOGO, LOGOS

console = Console(style="on grey11")


def _fullscreen_logo(logo: Text | str) -> Layout:
    """Build a full-screen layout with the Clinkey logo and branding.

    Parameters
    ----------
    logo : Text or str
        ASCII art to display as the title. Accepts a Rich ``Text`` object
        or a plain string.

    Returns
    -------
    rich.layout.Layout
        Layout instance that fills the terminal with the welcome screen.
    """
    logo_style = {
        "title_color": "bold light_green",
        "accent_color": "orchid1",
        "text_color": "grey100",
    }

    # Create the large ASCII art logo
    large_logo = logo

    # Create decorative elements
    decoration = Text(
        "═" * 60,
        style=logo_style["accent_color"],
    )

    # Create tagline
    tagline = Text.from_markup(
        "Your Own [bold light_green]SECRET BUDDY...[/]\n\n"
        "[dim white]... the perfect buddy we all need ![/]\n\n\n",
    )

    # Create prompt
    prompt = Text.from_markup(
        "\n\n\nPress [bold light_green]ENTER[/] to start generating passwords...",
        style="white",
    )

    # Combine all elements - each component centered individually using Align
    content = Group(
        Align.center(decoration),
        Text("\n\n"),
        Align.center(large_logo),
        Text("\n\n"),
        Align.center(decoration),
        Text("\n\n"),
        Align.center(tagline),
        Align.center(prompt),
    )

    # Create layout that fills the screen
    layout = Layout(name="middle")

    # Create the main panel
    main_panel = Panel(
        Align.center(content, vertical="middle"),
        box=box.DOUBLE,
        border_style=logo_style["accent_color"],
        padding=(2, 4),
        title="[bold orchid1]PASSWORD GENERATOR[/]",
        title_align="center",
        subtitle="[dim white]v1.2.0[/]",
        subtitle_align="center",
    )

    layout["middle"].update(main_panel)

    return layout

def rotate_logo(speed: float, fullscreen: bool = False):
    layout = None
    for logo in LOGOS:
        if fullscreen:
            layout = _fullscreen_logo(logo)
        else:
            layout = Align.center(logo)
        console.print(layout)
        sleep(speed)
        console.clear()

def reverse_logo(speed: float, fullscreen: bool = False):
    for logo in reversed(LOGOS):
        if fullscreen:
            layout = _fullscreen_logo(logo)
        else:
            layout = Align.center(logo)
        console.print(layout)
        sleep(speed)
        console.clear()

def animate_logo(fullscreen: bool = False):
    rotate_logo(0.07, fullscreen)
    rotate_logo(0.08, fullscreen)
    reverse_logo(0.08, fullscreen)
    reverse_logo(0.09, fullscreen)
    rotate_logo(0.1, fullscreen)
    rotate_logo(0.2, fullscreen)

def display_logo(fullscreen: bool = False):
    if fullscreen:
        layout = _fullscreen_logo(LOGO)
    else:
        layout = Align.center(LOGO)
    console.print(layout)


if __name__ == "__main__":
    animate_logo()
    display_logo()
    input()



    