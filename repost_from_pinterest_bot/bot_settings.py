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


# I don't want to set default values in the dataclass as that would lead to accepting possibly incomplete .yaml
def default_settings() -> BotSettings:
    return BotSettings(pinterest=BotSettings.Pinterest(queries=[], number_of_images=0),
                       posting=BotSettings.Posting(frequency_hours=0))


def load_settings(file_name) -> Optional[BotSettings]:
    """
    Loads settings from YAML file. If it is not found, creates one with default settings and returns them.
    :param file_name: path to settings file
    :return: BotSettings or None if file exist, but it's not a valid settings file
    """
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            loaded = yaml.load(file, Loader=yaml.SafeLoader)
            settings = BotSettingsSchema.load(loaded)
    except (yaml.YAMLError, marshmallow.exceptions.MarshmallowError) as e:
        logging.error(f"Failed to read settings: {e}")
        return None
    except FileNotFoundError as e:
        logging.warning(f"Settings are not loaded: {e}")
        settings = default_settings()
        try:
            save_settings(file_name, settings)
        except Exception as e:
            logging.error(f"Failed to write default settings to {file_name}: {e}")

    logging.info(f'Loaded settings: {settings}')
    return settings


def save_settings(file_name, settings: BotSettings):
    with open(file_name, 'w', encoding='utf-8') as file:
        yaml.dump(asdict(settings), file, allow_unicode=True)
