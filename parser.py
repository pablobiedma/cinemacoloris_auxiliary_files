import xml.etree.ElementTree as ET
import re
import json

# Function to extract image URLs
def extract_images(content):
    if content is None:
        return []
    return re.findall(r'<img.*?src="(.*?)"', content)

# Function to generate a clean excerpt
def extract_excerpt(content):
    if content is None:
        return ""
    text = re.sub(r'<.*?>', '', content)  # Remove HTML tags
    text = text.replace('\n', ' ').strip()
    return text[:150] + '...' if len(text) > 150 else text  # Limit excerpt length

# Function to generate a valid link from the title
def generate_link(title):
    title = title if title else "Untitled"
    return "post-" + re.sub(r'[^a-zA-Z0-9]+', '-', title.lower()).strip('-') + ".html"

# Load and parse the XML file
def parse_blogger_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    namespace = {'atom': 'http://www.w3.org/2005/Atom'}  # Define namespace
    entries = root.findall('.//atom:entry', namespace)
    
    posts = []
    for entry in entries:
        title_element = entry.find('atom:title', namespace)
        content_element = entry.find('atom:content', namespace)
        link_element = entry.find("atom:link[@rel='alternate']", namespace)
        
        title = title_element.text if title_element is not None else "Untitled"
        content = content_element.text if content_element is not None else ""
        link = link_element.attrib['href'] if link_element is not None else generate_link(title)
        images = extract_images(content)
        main_image = images[0] if images else "../images/default.jpg"  # Default image if none found
        excerpt = extract_excerpt(content)
        
        post_data = {
            "title": title,
            "excerpt": excerpt,
            "image": main_image,
            "images": images,
            "text": re.sub(r'<.*?>', '', content) if content else "",  # Full text without HTML tags
            "link": link
        }
        
        posts.append(post_data)
    
    return posts

# Example usage
file_path = "C:\\Users\\pablo\\Desktop\\cinemacoloris_auxiliary_files\\blog-12-13-2022.xml"
parsed_posts = parse_blogger_xml(file_path)

# Save output to a file
output_file = "C:\\Users\\pablo\\Desktop\\cinemacoloris_auxiliary_files\\parsed_posts.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(parsed_posts, f, ensure_ascii=False, indent=4)

print(f"Parsed data saved to {output_file}")
