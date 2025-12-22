# Optional Online STT (Phase 3.5 / T359)

TextAudio Edit is local-first by default. This document describes an **optional** online STT integration that can be enabled explicitly.

## Privacy note

Enabling online STT means the uploaded audio will be sent to a third-party service. Only enable this if you accept that tradeoff.

## Configuration

Set environment variables locally (do not commit secrets):

- `TEXTAUDIO_STT_BACKEND=online` enables the online backend (default is `local`)
- `TEXTAUDIO_ONLINE_STT_URL=<http(s) url>` endpoint that accepts raw WAV bytes
- `TEXTAUDIO_ONLINE_STT_AUTH_HEADER=<header value>` optional (e.g., `Bearer ...`)
- `TEXTAUDIO_ONLINE_STT_LANGUAGE=en` optional language hint (default `en`)

## Expected response shape

The backend expects the URL to return JSON in this shape:

```json
{
  "words": [
    { "text": "Hello", "start": 0.0, "end": 0.5 },
    { "text": "world", "start": 0.5, "end": 1.0 }
  ],
  "language": "en"
}
```

The backend converts this into the project `Transcript` token format (word + punctuation tokens) and validates that timestamps are monotonic and non-overlapping.

