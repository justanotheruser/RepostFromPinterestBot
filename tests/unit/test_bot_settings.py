import os.path

from repost_from_pinterest_bot.bot_settings import BotSettings, load_settings, save_settings


def test_no_settings_file(tmp_path):
    file_path = os.path.join(tmp_path, 'settings.yaml')
    bot_settings = load_settings(file_path)
    assert not os.path.exists(file_path)
    assert bot_settings is None


def test_save_and_load_settings(tmp_path):
    file_path = os.path.join(tmp_path, 'settings.yaml')
    settings = BotSettings(pinterest=BotSettings.Pinterest(queries=['мемы', 'природа'], number_of_images=5),
                           posting=BotSettings.Posting(frequency_hours=1))
    save_settings(file_path, settings)
    loaded_settings = load_settings(file_path)
    assert settings == loaded_settings


def test_load_incomplete_settings():
    file_path = os.path.join('tests', 'unit', 'invalid_settings__missing_number_of_images.yaml')
    bot_settings = load_settings(file_path)
    assert bot_settings is None


def test_remove_settings_by_passing_none(tmp_path):
    file_path = os.path.join(tmp_path, 'settings.yaml')
    settings = BotSettings(pinterest=BotSettings.Pinterest(queries=['мемы', 'природа'], number_of_images=5),
                           posting=BotSettings.Posting(frequency_hours=1))
    save_settings(file_path, settings)
    assert os.path.exists(file_path)
    save_settings(file_path, None)
    assert not os.path.exists(file_path)
