""" Defines the Config repository """

from models import Config, ConfigYear, ConfigYearHoliday

class ConfigRepository:
    """ The repository for the config model """

    @staticmethod
    def create_config(config_name):
        """ Creates a config """
        config = Config(config_name)
        return config.save()
    
    @staticmethod
    def create_config_year(config_id, year):
        """ Create a config year """
        config_year = ConfigYear(config_id, year)
        return config_year.save()
    
    @staticmethod
    def create_config_year_holiday(year, get_by, holiday_name, holiday_date):
        """ Create a config year holiday """
        config_year = ConfigYearHoliday(year, get_by, holiday_name, holiday_date)
        return config_year.save()

    @staticmethod
    def read_config(config_name):
        """ Query a config by config_name """
        config_query = Config.query.filter_by(config_name=config_name)
        return config_query.one() if config_query.count() == 1 else None
    
    @staticmethod
    def read_config_system_path(config_name):
        """ Query a config system path by config_name """
        config = ConfigRepository.read_config(config_name)
        return config.config_system_path if config and config.config_system_path else None
    
    @staticmethod
    def read_config_mail(config_name):
        """ Query a config mail by config_name """
        config = ConfigRepository.read_config(config_name)
        return config.config_mail if config and config.config_mail else None

    @staticmethod
    def read_config_year(year):
        """ Query a config year by year """
        config_year = ConfigYear.query.filter_by(year=year)
        return config_year.one() if config_year.count() == 1 else None

class ConfigsRepository:
    """ The repository for all configs """

    @staticmethod
    def read_configs():
        """ Query all configs """
        return Config.query.all()

    @staticmethod
    def read_config_year_holidays(year):
        """ Query all config year holidays """
        return ConfigYearHoliday.query.filter(ConfigYearHoliday.year == year).all()