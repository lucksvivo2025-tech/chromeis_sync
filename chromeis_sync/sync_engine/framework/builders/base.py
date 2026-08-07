class BaseBuilder:
    """
    Base Builder.

    Converts WHMCS data into an ERPNext payload.

    Child builders should implement build().
    """

    def __init__(self, source):
        self.source = source

    def build(self):
        raise NotImplementedError
