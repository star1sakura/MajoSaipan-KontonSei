import argparse
import pygame

from controller.game_controller import GameController
from model.character import CharacterId, get_all_characters


def _parse_character_id(name: str | None) -> CharacterId | None:
    if not name:
        return None
    token = name.strip().upper()
    for cid in CharacterId:
        if token == cid.name:
            return cid
    return None


def _prompt_character_id() -> CharacterId | None:
    chars = get_all_characters()
    if not chars:
        return None
    print("Select character:")
    for idx, preset in enumerate(chars, start=1):
        print(f"  {idx}. {preset.name} - {preset.description}")
    choice = input(f"Enter number [1-{len(chars)}] (blank = 1): ").strip()
    if not choice:
        return list(CharacterId)[0]
    if choice.isdigit():
        i = int(choice)
        if 1 <= i <= len(chars):
            return list(CharacterId)[i - 1]
    # fallback
    return list(CharacterId)[0]


def main():
    parser = argparse.ArgumentParser(description="Touhou-like STG")
    parser.add_argument(
        "-c",
        "--character",
        help="CharacterId name (e.g., REIMU_A, MARISA_A). Leave empty for prompt.",
    )
    args = parser.parse_args()

    # determine character id
    character_id = _parse_character_id(args.character)
    if character_id is None:
        character_id = _prompt_character_id()

    pygame.init()

    display_width = 720
    display_height = 640
    screen = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption("Touhou-like STG")

    controller = GameController(
        screen_width=display_width,
        screen_height=display_height,
        screen=screen,
        character_id=character_id,
        game_width=480
    )
    controller.run()


if __name__ == "__main__":
    main()
