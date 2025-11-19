import re

def extract_photo_src(html_photo: str):
  match = re.search(r'src=["\'](.*?)["\']', html_photo or '')
  photo_src = match.group(1) if match else None
  return photo_src