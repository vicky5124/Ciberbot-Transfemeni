from urllib.parse import ParseResult, urlparse
import typing as t


def uwuriparser(link: str) -> t.List[ParseResult]:
    # Initialise Empty Variables
    urls = []
    words = link.split()

    for word in words:
        # Check if last character is punctuation unlikely to be found as the last character in a URI
        if word[-1] in """!$&(*,;""":
            word = word[:-1]
        # Checks if the first character is an opening bracket or quotation mark, then checks if the last is too
        if word[0] in """(['‘"“{""":
            word = word[1:]
            if word[-1] in """)]'’"”}""":
                word = word[:-1]
        # Runs word against python's built-in URI checker

        parsed = urlparse(word)
        # If URI, Appends to List
        if parsed.netloc:
            urls.append(parsed)
    return urls
