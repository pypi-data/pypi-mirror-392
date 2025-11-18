import typing
import re

QUOTES={
    "de": {
        "open": '"`',
        "close": '"\''
    },
    "en": {
        "open": '``',
        "close": '\'\''
    }
}

class QuotesParser:

    def __init__(self, language="de"):
        self.opening = QUOTES[language]["open"]
        self.closing = QUOTES[language]["close"]
        self.reset_quotes()
        self.reset_linecounter()

    def reset_quotes(self):
        self.quotes_open = False

    def reset_linecounter(self):
        self.line_counter = 0

    def parse(self, lines: typing.Sequence[str]) -> typing.List[str]:
        outputakku = []
        for line in lines:
            outputakku.append(self.parseline(line))
        return outputakku

    def parseline(self, line: str) -> str:

        self.line_counter += 1
        if line.strip() == '' and self.quotes_open:
            print(
                f'Warning: End of paragraph found but quotes still open. Assuming close is missing. Line {self.line_counter}')
            self.quotes_open = False
        workline = line

        # Add guardian-chars in case string starts or ends with a quote.
        workline = 'x' + workline + 'x'

        # We go about replacing existing quotes by splitting the string with the
        # guardian-characters attached at the front and on the back by the existing
        # quotes. As some quotes might be done correctly, we use " '' "` and "'
        # as the quote characters.
        # But as quotes might be quoted by backslashes in tex, we do a negative-
        # lookbehind-match (?<!...)
        # To feature a little more readability, we construct the string from parts.
        theRe = '|'.join([
            '(?<!\\\\)"`',
            '(?<!\\\\)"\'',
            "(?<!\\\\)''",
            '(?<!\\\\)"'
        ])
        parts = re.split(theRe, workline)

        resultline = parts[0]
        for part in parts[1:]:
            resultline += self.closing if self.quotes_open else self.opening
            resultline += part
            self.quotes_open = not self.quotes_open

        # Remove the guards again
        resultline = resultline[1:-1]

        return resultline
