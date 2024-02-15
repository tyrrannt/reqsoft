import pathlib
import uuid
from datetime import datetime

from pytils.translit import slugify


def get_filename(filename, request):
    file_extension = pathlib.PurePosixPath(filename).suffix
    uid = uuid.uuid4()
    filename = str(uid) + file_extension
    return filename


def unique_slugify(instance, slug):
    """
    Генератор уникальных SLUG для моделей, в случае существования такого SLUG.
    """
    model = instance.__class__
    unique_slug = slugify(slug)
    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{unique_slug}-{uuid.uuid4().hex[:8]}'
    return unique_slug
