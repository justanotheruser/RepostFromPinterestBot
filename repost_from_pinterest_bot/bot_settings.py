from dataclasses import dataclass, field
from marshmallow_dataclass import class_schema
import yaml
from typing import Optional


@dataclass
class BotSettings:
    @dataclass
    class Pinterest:
        queries: list[str] = field(default_factory=list)
        number_of_images: int = 0

    @dataclass
    class Posting:
        frequency_hours: int = 0

    pinterest: Pinterest = Pinterest()
    posting: Posting = Posting()


BotSettingsSchema = class_schema(BotSettings)()


def load_settings(file_name) -> Optional[BotSettings]:
    with open(file_name, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        loaded = yaml.load(lines, Loader=yaml.SafeLoader)
        return BotSettingsSchema.load(loaded)


def save_settings(file_name, settings_dict):
    with open(file_name, 'w', encoding='utf-8') as file:
        yaml.dump(settings_dict, file)

