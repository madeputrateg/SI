import re

text = "pertanyan: halo jawabaan: kamu."

pattern = r"pertanyaan:(.*?)(?:jawabaan:|$)"
matches = re.findall(pattern, text, re.DOTALL)
for match in matches:
    print(match.strip())
secondpat=r"jawabaan:(.*)"
matches = re.findall(secondpat, text, re.DOTALL)
for match in matches:
    print(match.strip())