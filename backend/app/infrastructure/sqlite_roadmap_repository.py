from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

from backend.app.domain.roadmap_tracker import IterationRecord, RoadmapDocument, RoadmapMeta, SliceRecord


class SQLiteRoadmapRepository:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def save(self, document: RoadmapDocument) -> None:
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self._db_path) as connection:
            self._ensure_schema(connection)
            connection.execute("DELETE FROM roadmap_meta")
            connection.execute("DELETE FROM iterations")
            connection.execute("DELETE FROM slices")
            connection.execute(
                "INSERT INTO roadmap_meta (id, payload_json, updated_at) VALUES (?, ?, ?)",
                ("roadmap-meta", json.dumps(asdict(document.meta), ensure_ascii=False), document.meta.updated_at),
            )
            connection.executemany(
                """
                INSERT INTO iterations (id, title, status, goal, ordering, payload_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        record.id,
                        record.title,
                        record.status,
                        record.goal,
                        record.ordering,
                        json.dumps(asdict(record), ensure_ascii=False),
                        record.updated_at,
                    )
                    for record in document.iterations
                ],
            )
            connection.executemany(
                """
                INSERT INTO slices
                    (id, iteration_id, title, status, ordering, completed_at, payload_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        record.id,
                        record.iteration_id,
                        record.title,
                        record.status,
                        record.ordering,
                        record.completed_at,
                        json.dumps(asdict(record), ensure_ascii=False),
                        record.updated_at,
                    )
                    for record in document.slices
                ],
            )

    def load(self) -> RoadmapDocument:
        with sqlite3.connect(self._db_path) as connection:
            self._ensure_schema(connection)
            meta_row = connection.execute("SELECT payload_json FROM roadmap_meta WHERE id = ?", ("roadmap-meta",)).fetchone()
            if meta_row is None:
                raise FileNotFoundError(f"Roadmap database is empty: {self._db_path}")
            iterations = [
                IterationRecord(**json.loads(row[0]))
                for row in connection.execute("SELECT payload_json FROM iterations ORDER BY ordering, id")
            ]
            slices = [
                SliceRecord(**json.loads(row[0]))
                for row in connection.execute("SELECT payload_json FROM slices ORDER BY ordering, id")
            ]
            return RoadmapDocument(
                meta=RoadmapMeta(**json.loads(meta_row[0])),
                iterations=iterations,
                slices=slices,
            )

    def exists(self) -> bool:
        return self._db_path.exists()

    @staticmethod
    def _ensure_schema(connection: sqlite3.Connection) -> None:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS roadmap_meta (
                id TEXT PRIMARY KEY,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS iterations (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                goal TEXT NOT NULL,
                ordering INTEGER NOT NULL,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS slices (
                id TEXT PRIMARY KEY,
                iteration_id TEXT NOT NULL,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                ordering INTEGER NOT NULL,
                completed_at TEXT,
                payload_json TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
