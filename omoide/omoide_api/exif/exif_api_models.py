"""Web level API models."""

from typing import Any
from typing import Self

from pydantic import BaseModel
from pydantic import model_validator

from omoide import limits
from omoide import utils


class EXIFModel(BaseModel):
    """Input info for EXIF creation."""

    exif: dict[str, Any]

    model_config = {
        'json_schema_extra': {
            'examples': [
                {
                    'Make': 'SONY',
                    'Flash': 'Flash did not fire, auto mode',
                    'Model': 'DSC-S600',
                    'FNumber': 2.8,
                    'Contrast': 'Normal',
                    'DateTime': '2007:08:10 08:23:29',
                    'thumbnail': {
                        'ImageWidth': 512,
                        'ImageHeight': 384,
                    },
                }
            ]
        }
    }

    @model_validator(mode='after')
    def ensure_exif_is_not_too_big(self) -> Self:
        """Raise if given string is too big."""
        size = utils.get_size(self.exif)
        if size > limits.MAXIMUM_EXIF_SIZE:
            hr_size = utils.human_readable_size(size)
            hr_limit = utils.human_readable_size(limits.MAXIMUM_EXIF_SIZE)
            msg = f'Given EXIF is too big (got {hr_size}), ' f'allowed maximum is {hr_limit}'
            raise ValueError(msg)
        return self
