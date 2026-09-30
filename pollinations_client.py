import os
import urllib.parse
import requests

POLLINATIONS_BASE = "https://image.pollinations.ai/prompt/"
TIMEOUT_SECONDS = 60

# Prompts containing these words tend to make Pollinations generate a person
# wearing/holding the object rather than the bare object itself. Only these
# get the "no people, no hands" nudge — everything else stays untouched so
# generation quality/detail isn't diluted unnecessarily.
HUMAN_ASSOCIATED_KEYWORDS = {
    "shirt", "phone", "hat", "shoe", "shoes", "glove", "gloves",
    "watch", "glasses", "bag", "jacket", "dress", "pants", "jeans",
    "sock", "socks", "ring", "necklace", "helmet", "backpack",
}


def _build_prompt(prompt: str) -> str:
    prompt_lower = prompt.lower()
    if any(keyword in prompt_lower for keyword in HUMAN_ASSOCIATED_KEYWORDS):
        return f"{prompt}, no people, no hands"
    return prompt


def fetch_image(prompt: str, output_dir: str) -> str:
    """
    Requests a 2D image from Pollinations AI for the given prompt.
    Returns the local path to the saved PNG.
    Raises RuntimeError on network failure or bad response.
    """
    os.makedirs(output_dir, exist_ok=True)

    engineered_prompt = _build_prompt(prompt)
    encoded_prompt = urllib.parse.quote(engineered_prompt)
    url = f"{POLLINATIONS_BASE}{encoded_prompt}"

    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Pollinations request failed: {e}")

    if not response.headers.get("Content-Type", "").startswith("image"):
        raise RuntimeError("Pollinations did not return an image (possible rate limit or bad prompt).")

    image_path = os.path.join(output_dir, "input_2d.png")
    with open(image_path, "wb") as f:
        f.write(response.content)

    return image_path