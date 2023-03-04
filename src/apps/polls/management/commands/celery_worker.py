import shlex
import subprocess

from django.core.management.base import BaseCommand
from django.utils import autoreload


def restart_celery():
    celery_worker_cmd = 'celery -A core worker'
    cmd = f'pkill -f "{celery_worker_cmd}"'

    subprocess.call(shlex.split(cmd))
    subprocess.call(shlex.split(f'{celery_worker_cmd} --loglevel=info'))


class Command(BaseCommand):
    def handle(self, *args, **options):
        print('Starting celery worker with autoreload...')
        autoreload.run_with_reloader(restart_celery)
