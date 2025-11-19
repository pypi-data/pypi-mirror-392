import logging
from typing import Any, Type


def setup_logging(log_level: int = logging.INFO):
    """
    Setup logging for Tableclone
    """
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        level=log_level,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[console_handler],
    )


def get_logger(name):
    """Get logger for module"""
    logger = logging.getLogger(name)
    return logger


def merge_two_dicts(x, y):
    z = x.copy()  # start with keys and values of x
    z.update(y)  # modifies z with keys and values of y
    return z


def create_columns_if_not_exists(df, column_list):
    for col in column_list:
        if col not in df.columns.to_list():
            df[col] = None


class Option:
    def __init__(
        self,
        name: str,
        description: str,
        value_type: Type,
        default_value=None,
        required: bool = False,
        enum: list | None = None,
        incompatible_with: list["Option"] = [],
    ):
        """Describes an available option for Platformn, Object, Container or operation"""
        self.name = name
        self.description = description
        self.default_value = default_value
        self.value_type = value_type
        self.required = required
        self.enum = enum
        self.incompatible_with = incompatible_with

    def __str__(self) -> str:
        return self.name


class OptionSet:
    def __init__(self, options: list[Option]):
        """Set of available options"""
        self.options = options

    def __iter__(self):
        """Make the OptionSet iterable"""
        return iter(self.options)


class OptionValues:
    def __init__(self, option_set: OptionSet, option_values: dict[str, Any]):
        """List of option values, validated against an option set"""
        self.option_set = option_set
        self.values = option_values
        self.validate_option_values()

    def validate_option_values(self):
        """
        Checks that option_values are valid

        1. Checks that all required options are present
        2. Checks that all options exist in the option set
        3. Checks that all option values have the correct type
        4. Checks that incompatible options are not used together

        Args:
            option_values (dict): Dictionary of option values {option_name: option_value}
        """
        # Create a dictionary of options for quick lookup
        option_set_dict = {option.name: option for option in self.option_set}

        # Create a set of provided option names for quick lookup
        provided_options_names = set(self.values.keys())

        # Check that all required options are present
        for option in self.option_set:
            if option.required and option.name not in provided_options_names:
                raise (ValueError(f"Required option '{option.name}' is missing."))

        # Check that all provided options exist in the option set and have the correct type
        for name, value in self.values.items():
            if name not in option_set_dict:
                raise (ValueError(f"Unknown option '{name}'."))

            option = option_set_dict[name]
            if not isinstance(value, option.value_type):
                raise ValueError(
                    f"Option '{name}' has incorrect type. Expected {option.value_type.__name__}, got {type(value).__name__}."
                )
            # if enum is set, check that the value is in the enum
            if option.enum is not None:
                if value not in option.enum:
                    raise ValueError(
                        f"Option '{name}' has incorrect value. Expected one of {option.enum}, got {value}."
                    )

        # Check for incompatible options
        for name, option in option_set_dict.items():
            if name in provided_options_names:
                for incompatible_option in option.incompatible_with:
                    if incompatible_option.name in provided_options_names:
                        raise ValueError(
                            f"Incompatible options '{name}' and '{incompatible_option.name}' are both provided."
                        )

    def get(self, option: Option):
        """
        Returns the value of an option.
        """
        if option.name not in [option.name for option in self.option_set]:
            raise (ValueError(f"Unknown option '{option.name}'."))
        return self.values.get(option.name, option.default_value)
