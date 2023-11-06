import requests
import pandas as pd
from bs4 import BeautifulSoup
# import time

def get_wikipedia_content(species_name):
    try:
        url = f"https://en.wikipedia.org/wiki/{species_name.replace(' ', '_')}"

        # GET request
        response = requests.get(url)
        if response.status_code != 200:
            return "Error: Wikipedia page not found or other network issue."

        html_content = response.text

        # Parse HTML content
        soup = BeautifulSoup(html_content, 'html.parser')

        # Look for the 'Description' section first
        description_section = soup.find('span', id='Description')
        content_text = []

        if description_section:
            # Navigate to the parent <h2> tag and then to the next element
            current_tag = description_section.find_parent('h2').find_next_sibling()
            count = 0
            while current_tag and count < 3:
                if current_tag.name == 'ul':
                    for li in current_tag.find_all('li', recursive=False):
                        content_text.append(li.text.strip())
                        count += 1
                        if count >= 3:
                            break
                elif current_tag.name == 'p':
                    content_text.append(current_tag.text.strip())
                    count += 1
                elif current_tag.name == 'h2':
                    break
                current_tag = current_tag.find_next_sibling()
        else:
            # If 'Description' section not found, capture the initial paragraphs up to three or until next 'h2'
            current_tag = soup.find('p')
            count = 0
            while current_tag and count < 3:
                if current_tag.name == 'p' and current_tag.text.strip():
                    content_text.append(current_tag.text.strip())
                    count += 1
                if current_tag.name == 'h2':
                    break
                current_tag = current_tag.find_next_sibling()

        return '\n\n'.join(content_text)
    
    except Exception as e:
        return f"Error: {str(e)}"

file_path = 'sp_to_key.csv'
species_df = pd.read_csv(file_path)

total_species = len(species_df)

# Apply the function to the entire DataFrame
for i in range(len(species_df)):
    species_name = species_df.loc[i, 'species']
    print(f"Processing {i+1}/{total_species}: {species_name}... ", end="")
    species_df.loc[i, 'wikipedia_description'] = get_wikipedia_content(species_name)
    print("Done")
    # time.sleep(0.5)

# Save the updated DataFrame to a new CSV file
output_file_path = 'updated_sp_to_key_full.csv'
species_df.to_csv(output_file_path, index=False)
