import hashlib
import re
import typing as t
from collections import deque
from functools import cached_property
from pathlib import Path

import jmespath
from pydantic import AwareDatetime, BaseModel, computed_field

try:
    import orjson as json
except ImportError:
    import json  # type: ignore[no-redef]


class JournalEntry(BaseModel):
    type: str
    timestamp: AwareDatetime
    data: dict

    @computed_field
    @cached_property
    def key(self) -> str:
        return hashlib.md5(
            self.model_dump_json(exclude={'key'}).encode(),
            usedforsecurity=False,
        ).hexdigest()

    def __str__(self):
        return f'Entry [{self.key}]: {self.type}'

    def __hash__(self):
        return self.key

    def __setattr__(self, key, value):
        try:
            del self.key
        except AttributeError:
            pass
        return super().__setattr__(key, value)

    @classmethod
    def from_json(cls, data: str) -> "JournalEntry":
        try:
            raw_entry = json.loads(data)
        except json.JSONDecodeError as e:
            raise ValueError('Entry JSON is invalid') from e
        if not isinstance(raw_entry, dict):
            raise ValueError('Entry data is invalid')
        try:
            entry = {
                'type': raw_entry['event'],
                'timestamp': raw_entry['timestamp'],
                'data': raw_entry,
            }
        except KeyError:
            raise ValueError('Entry data is invalid')
        return cls.model_validate(entry)

    def search(self, path: str) -> str | None:
        return jmespath.search(path, self.model_dump(mode='json'))


class JournalFile:
    def __init__(self, path: str | Path):
        self.path = path
        self.last_mtime = 0.0
        self._entries: list[JournalEntry] = []

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, value: str | Path):
        if not isinstance(value, Path):
            value = Path(value)
        if not value.is_file():
            raise ValueError(f'File "{value}" does not exist')
        self._path = value

    @property
    def entries(self) -> t.Iterable[JournalEntry]:
        if self.last_mtime != (last_mtime := self.path.stat().st_mtime):
            self._entries = self._read()
            self.last_mtime = last_mtime
        return reversed(self._entries)

    def _read(self) -> list[JournalEntry]:
        entries = []
        for data in self.path.read_text().splitlines():
            try:
                event = JournalEntry.from_json(data)
            except ValueError:
                continue
            entries.append(event)
        return entries


class JournalDirectory:
    RE_LOGFILE = re.compile(
        r'^Journal\.[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6}\.[0-9]{2}\.log$'
    )

    def __init__(self, path: str | Path):
        self.path = path

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, value: str | Path):
        if not isinstance(value, Path):
            value = Path(value)
        if not value.is_dir():
            raise ValueError(f'Directory "{value}" does not exist')
        self._path = value

    @property
    def files(self) -> list[JournalFile]:
        files = []
        for fp in self.path.iterdir():
            if not self.RE_LOGFILE.match(fp.name):
                continue
            files.append(JournalFile(fp))
        return sorted(files, key=lambda f: f.path.name, reverse=True)


class JournalMonitor:
    CACHE_SIZE = 64

    def __init__(self, journal_dir: str | Path):
        self.journal_dir = JournalDirectory(journal_dir)
        self.recent_entries: deque[JournalEntry] = deque(maxlen=self.CACHE_SIZE)

    @property
    def last_entry(self) -> JournalEntry | None:
        try:
            return self.recent_entries[0]
        except IndexError:
            return None

    @last_entry.setter
    def last_entry(self, value: JournalEntry):
        self.recent_entries.appendleft(value)

    def _get_new_entries(self) -> list[JournalEntry]:
        new_entries: list[JournalEntry] = []
        for file in self.journal_dir.files:
            for entry in file.entries:
                if self.last_entry is None:
                    self.last_entry = entry
                    return new_entries
                if entry.timestamp < self.last_entry.timestamp:
                    return new_entries
                if entry == self.last_entry:
                    return new_entries
                new_entries.append(entry)
        return new_entries

    def iter_entries(self) -> t.Iterator[JournalEntry]:
        if not (new_entries := self._get_new_entries()):
            return
        for entry in reversed(new_entries):
            if entry in self.recent_entries:
                continue
            yield entry
            self.last_entry = entry
