import argparse
import feedparser
import json
import requests
import tempfile
import whisper

def get_args() -> tuple[str, str, bool]:
    parser = argparse.ArgumentParser(
                    prog='transcribe-podcast',
                    description='Transcribe audio files or podcasts using OpenAI Whisper')
    parser.add_argument("query")
    parser.add_argument("output")
    parser.add_argument("--fromfile", action="store_true")
    
    args = parser.parse_args()
    return (args.query, args.output, args.fromfile)

def get_feed_url(query: str) -> str:
    url = "https://itunes.apple.com/search"
    params = {
            'term': query,
            # TODO: don't hardcode this
            'country': 'gb',
            'entity': 'podcast'
            }
    
    response = requests.get(url, params=params)
    if (response.ok):
        jsonData = json.loads(response.content)
        results = jsonData["results"]

        print(f"Results for '{query}':")
        for i, item in enumerate(results):
            print(f"{i + 1}: {item["collectionName"]} by {item["artistName"]}")

        podcast_index = int(input("Please enter the index of the desired podcast feed: "))
        feed_url = results[podcast_index - 1]["feedUrl"]
        return feed_url
    else:
        response.raise_for_status()
        # TODO: feels improper
        return ""

def get_podcast_episode(query: str) -> str:
    feed_url = get_feed_url(query)
    feed = feedparser.parse(feed_url)
    feed_items = list(feed.entries)
    for i, entry in enumerate(feed_items):
        print(f"{i + 1} - {entry.title}")

    episode_index = int(input("Please enter the index of the desired podcast episode: "))
    feed_links = feed_items[episode_index - 1].links
    url = next((url.href for url in feed_links if ".mp3" in url.href), feed_links[0].href)
    return url

def parse_audio_file(filename: str) -> str:
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    return str(result["text"])

def main():
    # TODO: use is_file
    (query, output, is_file) = get_args()
    if not is_file:
        episode_url = get_podcast_episode(query)
        with tempfile.NamedTemporaryFile() as fp:
            print("Downloading file...")
            file_contents = requests.get(episode_url, stream=True).content

            fp.write(file_contents)

            print("Transcribing audio content...")
            transcription = parse_audio_file(fp.name)
            with open(output, "w") as f:
                f.write(transcription)

main()