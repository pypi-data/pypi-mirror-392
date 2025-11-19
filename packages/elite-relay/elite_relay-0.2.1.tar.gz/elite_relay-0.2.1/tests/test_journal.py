import datetime as dt
import json
import shutil
from pathlib import Path

import pytest

from elite_relay.journal import JournalEntry, JournalMonitor


@pytest.fixture(scope='session')
def journal_dir(data_dir, tmp_path_factory) -> Path:
    journal_dir = tmp_path_factory.mktemp('Elite Dangerous')
    shutil.copytree(data_dir, journal_dir, dirs_exist_ok=True)
    return journal_dir


@pytest.fixture
def journal_monitor(journal_dir) -> JournalMonitor:
    return JournalMonitor(journal_dir)


@pytest.fixture
def latest_journal(journal_dir) -> Path:
    return sorted(
        (f for f in journal_dir.iterdir() if f.name.startswith('Journal.')),
        key=lambda f: f.name,
        reverse=True,
    )[0]


@pytest.fixture
def write_entry(latest_journal, get_timestamp):
    def _write_entry(event: str, **kwargs) -> JournalEntry:
        data = json.dumps({'timestamp': get_timestamp(), 'event': event, **kwargs})
        entry = JournalEntry.from_json(data)
        with latest_journal.open('a') as f:
            f.write(data)
            f.write('\n')
        return entry

    yield _write_entry


def test_init(journal_monitor, write_entry):
    assert journal_monitor.last_entry is None
    entry = write_entry('FSDJump', StarSystem="Barnard's Star")
    assert list(journal_monitor.iter_entries()) == []
    assert journal_monitor.last_entry == entry


def test_new_entry(journal_monitor, write_entry):
    assert list(journal_monitor.iter_entries()) == []
    entry = write_entry('FSDJump', StarSystem='Sol')
    assert list(journal_monitor.iter_entries()) == [entry]


def test_duplicate_entries(journal_monitor, write_entry, get_timestamp):
    assert list(journal_monitor.iter_entries()) == []
    ts = get_timestamp()
    entries = [
        write_entry('FSDJump', timestamp=ts, StarSystem='Alpha Centauri')
        for _ in range(3)
    ]
    assert list(journal_monitor.iter_entries()) == [entries[0]]


def test_old_entry(journal_monitor, write_entry, format_timestamp):
    assert list(journal_monitor.iter_entries()) == []
    old_ts = journal_monitor.last_entry.timestamp - dt.timedelta(seconds=1)
    write_entry('FSDJump', timestamp=format_timestamp(old_ts))
    assert list(journal_monitor.iter_entries()) == []


def test_entry_key_determinism(write_entry, get_timestamp, format_timestamp):
    ts = dt.datetime.now()
    entry_a = write_entry('FSDJump', timestamp=format_timestamp(ts))
    entry_b = write_entry(
        'FSDJump', timestamp=format_timestamp(ts + dt.timedelta(seconds=1))
    )
    assert entry_a.key != entry_b.key

    ts = get_timestamp()
    entry_a = write_entry('FSDJump', timestamp=ts)
    entry_b = write_entry('FSDJump', timestamp=ts)
    assert entry_a.key == entry_b.key


def test_entry_key_update(write_entry, get_timestamp, format_timestamp):
    entry = write_entry('FSDJump')
    old_key = str(entry.key)
    entry.type = 'StartJump'
    assert entry.key != old_key
