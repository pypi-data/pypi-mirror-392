from dataclasses import dataclass


@dataclass(frozen=True)
class Heading:
    level: int
    text: str

    def __str__(self) -> str:
        return f"{'#' * self.level} {self.text}"

@dataclass(frozen=True)
class PureText:
    text: str

@dataclass(frozen=True)
class ItalicText:
    text: str

@dataclass(frozen=True)
class BoldText:
    text: str

@dataclass(frozen=True)
class LinkText:
    alt_text: str
    url: str

@dataclass(frozen=True)
class Image:
    alt_text: str
    url: str

@dataclass(frozen=True)
class InlineCodeText:
    text: str

@dataclass(frozen=True)
class Paragraph:
    content: list[PureText, ItalicText, BoldText, LinkText, Image, InlineCodeText]





