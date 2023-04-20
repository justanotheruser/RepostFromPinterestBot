import logging
from dataclasses import dataclass, asdict
from typing import Optional

import marshmallow
import yaml
from marshmallow_dataclass import class_schema


@dataclass
class BotSettings:
    @dataclass
    class Pinterest:
        queries: list[str]
        number_of_images: int

    @dataclass
    class Posting:
        frequency_hours: int

    pinterest: Pinterest
    posting: Posting


BotSettingsSchema = class_schema(BotSettings)()


def load_settings(file_name) -> Optional[BotSettings]:
    """
    Loads settings from YAML file
    :param file_name: path to settings file
    :return: BotSettings or None if file not found or not a valid settings file
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            loaded = yaml.load(file, Loader=yaml.SafeLoader)
            settings = BotSettingsSchema.load(loaded)
    except (yaml.YAMLError, marshmallow.exceptions.MarshmallowError) as e:
        logging.error(f"Invalid settings file: {e}")
        return None
    except FileNotFoundError as e:
        logging.warning(f"Settings file not found: {e}")
        return None

    logging.info(f'Loaded settings: {settings}')
    return settings


def save_settings(file_name, settings: BotSettings):
    with open(file_name, 'w', encoding='utf-8') as file:
        yaml.dump(asdict(settings), file, allow_unicode=True)
