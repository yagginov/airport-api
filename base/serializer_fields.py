from rest_framework.serializers import ChoiceField
from timezone_field.backends import get_tz_backend


class TimeZoneSerializerChoicesField(ChoiceField):
    def __init__(self, choices=None, **kwargs):
        self.use_pytz = kwargs.pop("use_pytz", None)
        self.tz_backend = get_tz_backend(self.use_pytz)

        if choices is None:
            self.choices = sorted(
                [str(self.tz_backend.to_tzobj(v)) for v in self.tz_backend.base_tzstrs]
            )
        else:
            self.choices = choices

        super().__init__(self.choices, **kwargs)
