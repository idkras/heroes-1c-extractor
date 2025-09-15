import trafilatura

def get_website_text_content(url):
    """
    Scrape and extract the main text content from a website.
    """
    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(downloaded)
    return text

if __name__ == "__main__":
    url = "https://garderob.app/garderob%20hypothises.md"
    content = get_website_text_content(url)
    
    if content:
        # Write the content to a file
        with open("garderob_hypothises_content.md", "w", encoding="utf-8") as f:
            f.write(content)
        print("Content successfully saved to garderob_hypothises_content.md")
    else:
        print("Failed to retrieve content from the URL.")