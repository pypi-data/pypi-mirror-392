from enum import Enum

_REGION_DATA = {
    "us-south": {
        "watsonxai": "https://us-south.ml.cloud.ibm.com",
        "openscale": "https://api.aiopenscale.cloud.ibm.com",
        "factsheet": None,
    },
    "eu-de": {
        "watsonxai": "https://eu-de.ml.cloud.ibm.com",
        "openscale": "https://eu-de.api.aiopenscale.cloud.ibm.com",
        "factsheet": "frankfurt",
    },
    "au-syd": {
        "watsonxai": "https://au-syd.ml.cloud.ibm.com",
        "openscale": "https://au-syd.api.aiopenscale.cloud.ibm.com",
        "factsheet": "sydney",
    },
}


class Region(str, Enum):
    """
    Supported IBM watsonx.governance regions.

    Defines the available regions where watsonx.governance SaaS
    services are deployed.

    Attributes:
        US_SOUTH (str): "us-south".
        EU_DE (str): "eu-de".
        AU_SYD (str): "au-syd".
    """

    US_SOUTH = "us-south"
    EU_DE = "eu-de"
    AU_SYD = "au-syd"

    @property
    def watsonxai(self):
        return _REGION_DATA[self.value]["watsonxai"]

    @property
    def openscale(self):
        return _REGION_DATA[self.value]["openscale"]

    @property
    def factsheet(self):
        return _REGION_DATA[self.value]["factsheet"]

    @classmethod
    def from_value(cls, value: str) -> "Region":
        if value is None:
            return cls.US_SOUTH

        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            try:
                return cls(value.lower())
            except ValueError:
                raise ValueError(
                    "Invalid value for parameter 'region'. Received: '{}'. Valid values are: {}.".format(
                        value, [item.value for item in Region]
                    )
                )

        raise TypeError(
            f"Invalid type for parameter 'region'. Expected str or Region, but received {type(value).__name__}."
        )


class TaskType(Enum):
    QUESTION_ANSWERING = "question_answering"
    SUMMARIZATION = "summarization"
    RETRIEVAL_AUGMENTED_GENERATION = "retrieval_augmented_generation"
    CLASSIFICATION = "classification"
    GENERATION = "generation"
    CODE = "code"
    EXTRACTION = "extraction"

    @classmethod
    def from_value(cls, value: str) -> "TaskType":
        if isinstance(value, cls):
            return value

        if isinstance(value, str):
            try:
                return cls(value.lower())
            except ValueError:
                raise ValueError(
                    "Invalid value for parameter 'task_id'. Received: '{}'. Valid values are: {}.".format(
                        value, [item.value for item in TaskType]
                    )
                )

        raise TypeError(
            f"Invalid type for parameter 'task_id'. Expected str or TaskType, but received {type(value).__name__}."
        )
