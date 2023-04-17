import os.path

from repost_from_pinterest_bot.bot_settings import load_settings, save_settings, empty_settings


def test_no_settings_file(tmp_path):
    file_path = os.path.join(tmp_path, 'settings.yaml')
    bot_settings = load_settings(file_path)
    assert os.path.exists(file_path)
    assert bot_settings == empty_settings()


def test_save_and_load_settings(tmp_path):
    file_path = os.path.join(tmp_path, 'settings.yaml')
    settings = empty_settings()
    settings.pinterest.queries = ['мемы', 'природа']
    settings.pinterest.number_of_images = 5
    settings.posting.frequency_hours = 1
    save_settings(file_path, settings)
    loaded_settings = load_settings(file_path)
    assert settings == loaded_settings


def test_load_incomplete_settings():
    file_path = os.path.join('tests', 'unit', 'invalid_settings__missing_number_of_images.yaml')
    bot_settings = load_settings(file_path)
    assert bot_settings is None
