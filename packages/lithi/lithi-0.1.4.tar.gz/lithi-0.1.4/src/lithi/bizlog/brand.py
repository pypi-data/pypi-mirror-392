"""Module for the applications's brand."""


def get_name() -> str:
    """Get the application name."""
    return "lithi"


def get_logo() -> str:
    """Get the printable logo."""
    logo = (
        ""
        "  ░█░░░▀█▀░▀█▀░█░█░▀█▀\n"
        "  ░█░░░░█░░░█░░█▀█░░█░\n"
        "  ░▀▀▀░▀▀▀░░▀░░▀░▀░▀▀▀\n"
    )
    logo += "ELF parser and memory live inspector\n"
    return logo
