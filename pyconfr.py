import json
from pathlib import Path

from babel.dates import format_date, format_time, format_timedelta
from datetime import date, time, timedelta
from flask import Flask, Response, render_template, url_for
from flask_frozen import Freezer
from flask_weasyprint import render_pdf
from markdown2 import Markdown
from slugify import slugify

YEAR = 2026

app = Flask(__name__, static_url_path=f'/{YEAR}/static')
_GIT_MAIN = Path(app.root_path) / '.git' / 'refs' / 'heads' / 'main'
GIT_VERSION = _GIT_MAIN.read_text().strip()[:7]


@app.template_filter()
def slug(string):
    return slugify(string, max_length=30)


@app.template_filter()
def format_duration(minutes):
    return format_timedelta(
        timedelta(seconds=minutes*60), threshold=10, format='short')


@app.template_filter()
def format_day(day, lang):
    day_date = date.fromisoformat(day)
    return format_date(day_date, format='full', locale=lang)


@app.template_filter()
def format_minutes(minutes, lang):
    hour_time = time(int(minutes) // 60, int(minutes) % 60)
    return format_time(hour_time, format='short', locale=lang)


@app.template_filter()
def markdown(string):
    return Markdown().convert(string)


@app.template_filter()
def ical_datetime(string):
    return string.replace('-', '').replace(':', '').split('+')[0]


@app.template_filter()
def ical_text(string):
    return string.replace('\n', '\n\t')


@app.template_filter()
def version(url):
    return f'{url}?{GIT_VERSION}'


@app.route('/')
@app.route(f'/{YEAR}/')
@app.route(f'/{YEAR}/<lang>/')
@app.route(f'/{YEAR}/<lang>/<name>.html')
def page(name='index', lang='fr'):
    return render_template(
        f'{lang}/{name}.jinja2.html', page_name=name, lang=lang)


@app.cli.command('freeze')
def freeze():
    Freezer(app).freeze()
