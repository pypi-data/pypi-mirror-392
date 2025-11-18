from .sample_mean import SampleMean
from .sample_prop import SampleProp

class AB:
    """
    AB-testing
    """
    def __init__(self, data,  days=1, alpha=0.05, beta=0.20, name='AB-testing'):
        self.name = name
        self.days = days
        self.alpha = alpha
        self.beta = beta
        self.data_input = data
        self.group_list = []
        self.data_output = []
        self.report = ''


__all__ = ['AB']
