# Transcribe Podcast

This is a basic Python script to automate searching for a podcast and transcribing a desired episode.

## Usage

Dependency management is handled via nix - if you do not use nix then you're on your own!

The main entrypoint of the program is `main.py`. Standard usage would be something like

```sh 
python main.py "Cool Podcast" output.txt
```

There is also a `--fromfile` flag for if you wish to transcribe a file. Usage for that would be something like

```sh 
python main.py "/home/user/podcast.mp3" output.txt --from-file
```

## Areas off improvement

Currently everything is very hardcoded and probably doesn't handle errors well. There are also a couple of TODOs.
