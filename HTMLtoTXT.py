from bs4 import BeautifulSoup

#Loading the HTML transcript
with open("transcript.html", "r", encoding="utf-8") as f:
    html_content = f.read()

#Parsing
soup = BeautifulSoup(html_content, "html.parser")
text = soup.get_text(separator="\n")

#Saved to txt
with open("transcript.txt", "w", encoding="utf-8") as f:
    f.write(text)

print("Transcript converted to transcript.txt")


