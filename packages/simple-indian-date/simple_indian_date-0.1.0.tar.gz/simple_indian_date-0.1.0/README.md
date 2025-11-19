# simple-indian-date

A tiny Python library that converts dates into common Indian date formats.

## Install

pip install simple-indian-date

## Usage

from datetime import datetime
from simple_indian_date import to_dd_mm_yyyy

print(to_dd_mm_yyyy(datetime.now()))
