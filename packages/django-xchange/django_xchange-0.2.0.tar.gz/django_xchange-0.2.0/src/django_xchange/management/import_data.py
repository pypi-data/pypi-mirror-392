import sys
from pathlib import Path

from django.core.management import BaseCommand, call_command
from django.utils.translation import gettext as _

from django_xchange.management.utils import PrintCommandMixin
from django_xchange.utils import import_csv


class Command(PrintCommandMixin, BaseCommand):
    help = _('Import rates from csv file')

    def handle(self, *args, **options) -> None:
        call_command('migrate')

        path = Path(__file__).parents[4] / 'examples/example_rates.csv'
        if not path.exists():
            self.print('ERROR', f'File {path} does not exist', exit_code=1)
            sys.exit(1)
        results = import_csv(path)
        self.print(
            'WARNING' if results['skipped'] else 'SUCCESS',
            _('Loaded %(loaded)s records. Skipped %(skipped)s records' % results),
            exit_code=2 if results['skipped'] else 0,
        )
