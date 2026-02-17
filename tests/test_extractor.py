from crawler.extractor import extract_a_hrefs


def test_extract_only_a_href():
    html = '''
    <html>
      <body>
        <a href="/a">A</a>
        <a href="https://b.com">B</a>
        <img src="https://img.com/1.png" />
        <script src="https://cdn.com/x.js"></script>
      </body>
    </html>
    '''
    got = extract_a_hrefs(html)
    assert got == ["/a", "https://b.com"]
