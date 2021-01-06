"""Base use case"""


class BaseUseCase:
    """
    Base implementation to use cases
    """

    def execute(self):
        """
        Execute both validation and use case

        :return:
        """
        self.validation()
        self.use_case()

    def validation(self):
        """
        Run validation in models

        :return:
        """

    def use_case(self):
        """
        Run use case

        :return:
        """
