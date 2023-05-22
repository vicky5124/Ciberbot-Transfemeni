from urllib.parse import urlparse
def uwuriparser(link: str):
    urls = []
    words = link.split()
    posa = 0
    posb = 0
    for word in words:
        if word[len(word)-1] in '''!$&(*,;''':
            posb += 1
        if (word[0] in '''(['"{''') and (word[len(word)-(posb+1)] in ''')]'"}'''):
            posa +=1
            posb += 1
        parsed = urlparse(word[posa:-posb])
        if parsed.netloc:
            urls.append(word)
    return(urls)