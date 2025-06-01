from bs4 import BeautifulSoup

def convert_html_to_txt(html_file="transcript.html", txt_file="transcript.txt"):
    with open(html_file, "r", encoding="utf-8") as f:
        html_content = f.read()

    soup = BeautifulSoup(html_content, "html.parser")
    text = soup.get_text(separator="\n")

    with open(txt_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"Transcript converted to {txt_file}")