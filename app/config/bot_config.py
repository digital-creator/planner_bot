import configparser
import os


config = configparser.ConfigParser()


def get_config(section, name, config=config):
    config.read("config.ini", encoding='utf-8')
    return config[section][name]


def set_config(section, name, value, config=config):
    config[section] = {name: value}
    with open('config.ini', 'w', encoding='utf-8') as file:
        config.write(file)


if __name__ == "__main__":
    os.chdir('../..')
    print('путь конфига: ', os.getcwd())
