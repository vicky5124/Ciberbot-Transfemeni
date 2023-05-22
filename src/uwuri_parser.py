from urllib.parse import urlparse
import typing as t


def uwuriparser(link: str) -> t.List[str]:
    # Initialise Empty Variables
    urls = []
    words = link.split()
    posa = 0
    posb = 0
    for word in words:
        # Check if last character is punctuation unlikely to be found as the last character in a URI
        if word[len(word) - 1] in """!$&(*,;""":
            posb += 1
        # Checks if the first character is an opening bracket or quotation mark, then checks if the last is too
        if word[0] in """(['‘"“{""":
            posa += 1
        if word[len(word) - (posb + 1)] in """)]'’"”}""":
            posb += 1
        # Runs word against python's built-in URI checker
        parsed = urlparse(word[posa:-posb])
        # If URI, Appends to List
        if parsed.netloc:
            urls.append(word)
    return urls
