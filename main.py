import argparse
import feedparser
import json
import requests
import tempfile
import whisper


def get_args() -> tuple[str, str, bool]:
    parser = argparse.ArgumentParser(
        prog="transcribe-podcast",
        description="Transcribe audio files or podcasts using OpenAI Whisper",
    )
    parser.add_argument("query")
    parser.add_argument("output")
    parser.add_argument("--from-file", action="store_true")

    args = parser.parse_args()
    return (args.query, args.output, args.from_file)


def get_feed_url(query: str) -> str:
    url = "https://itunes.apple.com/search"
    params = {
        "term": query,
        # TODO: don't hardcode this
        "country": "gb",
        "entity": "podcast",
    }

    response = requests.get(url, params=params)
    if response.ok:
        jsonData = json.loads(response.content)
        results = jsonData["results"]

        print(f"Results for '{query}':")
        for i, item in enumerate(results):
            print(f"{i + 1}: {item["collectionName"]} by {item["artistName"]}")

        podcast_index = int(
            input("Please enter the index of the desired podcast feed: ")
        )
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

    items = feed_items
    episode_index = 0
    searching = True
    while searching:
        for i, entry in enumerate(items):
            print(f"{i + 1} - {entry.title}")
        episode_index_or_search = input(
            "Please enter the index of the desired podcast episode or a keyword to search (type 'all' to view all podcasts from feed): "
        )
        try:
            episode_index = int(episode_index_or_search)
            searching = False
        except ValueError:
            if episode_index_or_search == "all":
                items = feed_items
                break

            filtered_items = []
            for entry in feed_items:
                if episode_index_or_search.lower() in entry.title.lower():
                    filtered_items.append(entry)
            items = filtered_items

    feed_links = items[episode_index - 1].links
    url = next(
        (url.href for url in feed_links if ".mp3" in url.href), feed_links[0].href
    )
    return url


def parse_audio_file(filename: str) -> str:
    print("Transcribing audio content...")
    model = whisper.load_model("base")
    result = model.transcribe(filename)
    return str(result["text"])


def main():
    (query, output, from_file) = get_args()
    transcription = ""

    if from_file:
        transcription = parse_audio_file(query)
    else:
        episode_url = get_podcast_episode(query)
        with tempfile.NamedTemporaryFile() as fp:
            print("Downloading file...")
            file_contents = requests.get(episode_url, stream=True).content
            fp.write(file_contents)
            transcription = parse_audio_file(fp.name)

    with open(output, "w") as f:
        f.write(transcription)


main()
