import csv
import importlib
import io
import json
from pathlib import Path

from django.core.files.uploadedfile import UploadedFile

from django_xchange.models import Rate


def resolve_fqn(klass: str) -> object:
    module_path, class_name = klass.rsplit('.', 1)

    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def import_csv(uploaded_file: UploadedFile | str | Path) -> dict[str, int]:
    """Upload the CSV file of Rates."""
    if isinstance(uploaded_file, str):
        decoded_file = Path(uploaded_file).read_text(encoding='utf-8')
    elif isinstance(uploaded_file, Path):
        decoded_file = uploaded_file.read_text(encoding='utf-8')
    else:
        decoded_file = uploaded_file.read().decode('utf-8')
    io_string = io.StringIO(decoded_file)

    results = {
        'loaded': 0,
        'skipped': 0,
    }

    dialect = csv.Sniffer().sniff(io_string.read(1024))
    io_string.seek(0)
    reader = csv.reader(io_string, dialect=dialect)
    for i, row in enumerate(reader):
        if i == 0:
            headers = row
        else:
            data = dict(zip(headers, row, strict=False))
            _, created = Rate.objects.get_or_create(day=data['day'], defaults={'rates': json.loads(data['rates'])})
            if created:
                results['loaded'] += 1
            else:
                results['skipped'] += 1
    return results
