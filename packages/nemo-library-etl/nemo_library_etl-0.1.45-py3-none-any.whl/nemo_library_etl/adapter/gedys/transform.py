"""
Gedys ETL Transform Module.

This module handles the transformation phase of the Gedys ETL pipeline.
It processes the extracted data, applies business rules, data cleaning, and formatting
to prepare the data for loading into the target system.

The transformation process typically includes:
1. Data validation and quality checks
2. Data type conversions and formatting
3. Business rule application
4. Data enrichment and calculated fields
5. Data structure normalization
6. Comprehensive logging throughout the process

Classes:
    GedysTransform: Main class handling Gedys data transformation.
"""

import logging
import re
from typing import Union
from nemo_library_etl.adapter._utils.db_handler_local import ETLDuckDBHandler
from nemo_library_etl.adapter.gedys.config_models_gedys import ConfigGedys
from nemo_library_etl.adapter._utils.enums import ETLAdapter, ETLStep
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary


class GedysTransform:
    """
    Handles transformation of extracted Gedys data.

    This class manages the transformation phase of the Gedys ETL pipeline,
    providing methods to process, clean, and format the extracted data for loading
    into the target system.

    The transformer:
    - Uses NemoLibrary for core functionality and configuration
    - Integrates with Prefect logging for pipeline visibility
    - Applies business rules and data validation
    - Handles data type conversions and formatting
    - Provides data enrichment and calculated fields
    - Ensures data quality and consistency

    Attributes:
        nl (NemoLibrary): Core Nemo library instance for system integration.
        config: Configuration object from the Nemo library.
        logger: Prefect logger for pipeline execution tracking.
        cfg (PipelineGedys): Pipeline configuration with transformation settings.
    """

    def __init__(
        self,
        nl: NemoLibrary,
        cfg: ConfigGedys,
        logger: Union[logging.Logger, object],
        fh: ETLFileHandler,
        local_database: ETLDuckDBHandler,
    ) -> None:
        """
        Initialize the Gedys Transform instance.

        Sets up the transformer with the necessary library instances, configuration,
        and logging capabilities for the transformation process.

        Args:
            nl (NemoLibrary): Core Nemo library instance for system integration.
            cfg (PipelineGedys): Pipeline configuration object containing
                                                          transformation settings and rules.
            logger (Union[logging.Logger, object]): Logger instance for recording execution details.
                                                   Can be a standard Python logger or Prefect logger.
        """
        self.nl = nl
        self.cfg = cfg
        self.logger = logger
        self.fh = fh
        self.local_database = local_database

        super().__init__()

    def transform(self) -> None:
        """Transform Gedys Opportunity data in Python and write an English-only wide table with start_<phase> columns."""
        import re
        from collections import defaultdict
        import pandas as pd

        self.logger.info("Transforming all Gedys objects (Python, EN-only columns)")

        NBSP = "\u00a0"

        def norm(s: str) -> str:
            """Normalize labels: strip quotes, replace NBSP, collapse spaces, strip; return None for empty."""
            if s is None:
                return None
            # ensure string
            s = str(s)

            # replace non-breaking spaces
            s = s.replace("\u00a0", " ")

            # trim outer quotes repeatedly: "foo", 'foo',  „foo“  etc.
            # do it in a loop in case the value is double-quoted like "\"Abschluss\""
            while len(s) >= 2:
                first, last = s[0], s[-1]
                if (first == last) and first in ("'", '"', "„", "“", "‚", "’"):
                    s = s[1:-1]
                else:
                    break

            # collapse internal whitespace and trim
            import re

            s = re.sub(r"\s+", " ", s).strip()

            return s or None

        def to_ident(s: str) -> str:
            """Turn a phase name into a safe SQL identifier (lowercase with underscores)."""
            s = norm(s) or ""
            s = re.sub(r"[^A-Za-z0-9_]+", "_", s)
            if re.match(r"^[0-9]", s):
                s = "_" + s
            return s.lower()

        def parse_ts(x):
            """Parse timestamps to pandas.Timestamp (UTC-aware if possible)."""
            if x is None:
                return pd.NaT
            return pd.to_datetime(x, utc=True, errors="coerce")

        # --- 1) Load minimal fields + history from DuckDB ---
        rows = self.local_database.con.execute(
            """
            SELECT
                Oid,
                Created,
                ClosingDate,
                ExpectedTurnover,
                Currency.Language_en                 AS Currency,
                Status.Language_en                   AS Status,
                Status.TargetProbability.Language_en AS TargetProbability,
                Phase.Language_de                    AS Phase_DE,
                Phase.Language_en                    AS Phase_EN,
                Reason.Language_en                   AS Reason,
                RequirementsDescription,
                Subject,
                Common_EntityTitle,
                Probability.Language_en              AS Probability,
                _RecordHistory                        AS History
            FROM Opportunity
        """
        ).fetchall()

        opps = []
        for (
            oid,
            created,
            closing,
            expected,
            currency,
            status,
            target_prob,
            phase_de,
            phase_en,
            reason,
            req_desc,
            subject,
            title,
            prob,
            history,
        ) in rows:
            opps.append(
                {
                    "Oid": oid,
                    "Created": parse_ts(created),
                    "ClosingDate": closing,
                    "ExpectedTurnover": expected,
                    "Currency": currency,
                    "Status": status,
                    "TargetProbability": target_prob,
                    "Phase_DE": norm(phase_de),
                    "Phase_EN": norm(phase_en),
                    "Reason": reason,
                    "RequirementsDescription": req_desc,
                    "Subject": subject,
                    "Common_EntityTitle": title,
                    "Probability": prob,
                    "History": history or [],
                }
            )
        self.logger.info(f"Loaded {len(opps)} opportunities")

        # --- 2) Build DE->EN map + EN set from current records (ground truth for English names) ---
        de_to_en = {}
        en_set = set()
        for o in opps:
            de = o["Phase_DE"]
            en = o["Phase_EN"]
            if de and en:
                de_to_en[de] = en
                en_set.add(en)
            elif en:
                en_set.add(en)

        def to_en(label: str) -> str:
            """Return English label or None. DE -> EN via map; EN passes; unknown -> None."""
            lab = norm(label)
            if not lab:
                return None
            if lab in de_to_en:  # german key -> map to english
                return de_to_en[lab]
            if lab in en_set:  # already known english
                return lab
            return None  # drop unknowns to avoid german leaks

        # --- 3) Build events per OID: initial (from first OLD) + all NEW changes (both mapped to EN) ---
        events_by_oid = defaultdict(list)

        for o in opps:
            oid = o["Oid"]
            created_ts = o["Created"]
            history = o["History"] or []

            earliest_change_ts = None
            earliest_old_en = None
            has_change = False

            # Iterate history; collect NEW events; track earliest OLD
            for h in history:
                h_ts = parse_ts((h or {}).get("Created"))
                infos = (h or {}).get("AdditionalInfo") or []
                for info in infos:
                    field = norm(str((info or {}).get("FieldName")))
                    if field != "Phase":
                        continue
                    new_en = to_en((info or {}).get("NewValue"))
                    old_en = to_en((info or {}).get("OldValue"))

                    if new_en:
                        events_by_oid[oid].append((new_en, h_ts))
                        has_change = True

                    if h_ts is not None:
                        if earliest_change_ts is None or h_ts < earliest_change_ts:
                            earliest_change_ts = h_ts
                            earliest_old_en = old_en

            # Seed initial phase at Created from earliest OLD (if present and mapped)
            if earliest_old_en and created_ts is not None and not pd.isna(created_ts):
                events_by_oid[oid].append((earliest_old_en, created_ts))

            # If no change entries at all, seed with current phase (EN) at Created
            if not has_change:
                cur_en = to_en(o["Phase_EN"]) or to_en(o["Phase_DE"])
                if cur_en and created_ts is not None and not pd.isna(created_ts):
                    events_by_oid[oid].append((cur_en, created_ts))

        # === DEBUG BLOCK: inspect history labels and event derivation (no side effects on final table) ===
        import pandas as pd

        dbg_rows = []  # raw history rows with mapping
        ev_rows = []  # derived events rows (initial from OLD, changes from NEW)

        for o in opps:
            oid = o["Oid"]
            created_ts = o["Created"]
            history = o["History"] or []

            # collect raw history rows (only FieldName='Phase')
            # and track earliest change for initial OLD-phase
            earliest_change_ts = None
            earliest_old_en = None
            has_change = False

            for h in history:
                h_ts = parse_ts((h or {}).get("Created"))
                infos = (h or {}).get("AdditionalInfo") or []
                for info in infos:
                    field = norm(str((info or {}).get("FieldName")))
                    if field != "Phase":
                        continue
                    new_raw = norm((info or {}).get("NewValue"))
                    old_raw = norm((info or {}).get("OldValue"))
                    new_en = to_en(new_raw)
                    old_en = to_en(old_raw)

                    dbg_rows.append(
                        {
                            "oid": oid,
                            "created_ts": created_ts,
                            "h_ts": h_ts,
                            "field": field,
                            "old_raw": old_raw,
                            "new_raw": new_raw,
                            "old_en": old_en,
                            "new_en": new_en,
                        }
                    )

                    if new_en:
                        # this would create a NEW event (phase entered at h_ts)
                        ev_rows.append(
                            {
                                "oid": oid,
                                "phase_en": new_en,
                                "ts": h_ts,
                                "source": "history_new",
                            }
                        )
                        has_change = True

                    # track earliest change and its OLD
                    if h_ts is not None:
                        if earliest_change_ts is None or h_ts < earliest_change_ts:
                            earliest_change_ts = h_ts
                            earliest_old_en = old_en

            # initial event from earliest OLD at Created
            if earliest_old_en and created_ts is not None and not pd.isna(created_ts):
                ev_rows.append(
                    {
                        "oid": oid,
                        "phase_en": earliest_old_en,
                        "ts": created_ts,
                        "source": "initial_from_old",
                    }
                )

            # fallback: no change at all -> seed with current phase at Created
            if not has_change:
                cur_en = to_en(o["Phase_EN"]) or to_en(o["Phase_DE"])
                if cur_en and created_ts is not None and not pd.isna(created_ts):
                    ev_rows.append(
                        {
                            "oid": oid,
                            "phase_en": cur_en,
                            "ts": created_ts,
                            "source": "seed_current_when_no_change",
                        }
                    )

        # Put debug frames into DuckDB for easy querying
        dbg_hist_df = pd.DataFrame(dbg_rows)
        dbg_ev_df = pd.DataFrame(ev_rows)

        self.local_database.con.register("tmp_dbg_hist", dbg_hist_df)
        self.local_database.con.execute(
            "CREATE OR REPLACE TABLE debug_phase_history AS SELECT * FROM tmp_dbg_hist"
        )
        self.local_database.con.unregister("tmp_dbg_hist")

        self.local_database.con.register("tmp_dbg_ev", dbg_ev_df)
        self.local_database.con.execute(
            "CREATE OR REPLACE TABLE debug_phase_events AS SELECT * FROM tmp_dbg_ev"
        )
        self.local_database.con.unregister("tmp_dbg_ev")

        # Quick summaries in logs

        # 1) Unknown labels that to_en() dropped
        unknowns = self.local_database.con.execute(
            """
            WITH labels AS (
                SELECT CAST(old_raw AS VARCHAR) AS lbl FROM debug_phase_history WHERE old_raw IS NOT NULL
                UNION ALL
                SELECT CAST(new_raw AS VARCHAR) AS lbl FROM debug_phase_history WHERE new_raw IS NOT NULL
            ),
            mapped AS (
                SELECT
                    lbl,
                    CASE
                        WHEN lbl IN (SELECT CAST(old_en AS VARCHAR) FROM debug_phase_history WHERE old_en IS NOT NULL)
                            OR lbl IN (SELECT CAST(new_en AS VARCHAR) FROM debug_phase_history WHERE new_en IS NOT NULL)
                        THEN 'en'
                        ELSE 'unknown'
                    END AS status
                FROM labels
            )
            SELECT lbl, COUNT(*) AS cnt
            FROM mapped
            WHERE status = 'unknown'
            GROUP BY 1
            ORDER BY cnt DESC, lbl ASC
        """
        ).fetchall()
        if unknowns:
            self.logger.warning("Unknown phase labels (not mapped to EN):")
            for lbl, cnt in unknowns[:20]:
                self.logger.warning(f"  - {lbl!r}  (x{cnt})")
        else:
            self.logger.info(
                "No unknown phase labels. All history labels mapped to EN."
            )

        # 2) Which OIDs have both Development and Closure events?
        both_dc = self.local_database.con.execute(
            """
            WITH flags AS (
                SELECT
                    oid,
                    MAX(CASE WHEN LOWER(phase_en) = 'development' THEN 1 ELSE 0 END) AS has_dev,
                    MAX(CASE WHEN LOWER(phase_en) = 'closure'     THEN 1 ELSE 0 END) AS has_clo
                FROM debug_phase_events
                GROUP BY oid
            )
            SELECT oid FROM flags WHERE has_dev = 1 AND has_clo = 1
            ORDER BY oid
        """
        ).fetchall()
        self.logger.info(
            f"OIDs with BOTH Development and Closure in derived events: {len(both_dc)}"
        )
        for (oid,) in both_dc[:20]:
            self.logger.info(f"  - {oid}")

        # 3) For one example OID (if any), print the full timeline
        if both_dc:
            example_oid = both_dc[0][0]
            rows_tl = self.local_database.con.execute(
                f"""
                SELECT oid, ts, phase_en, source
                FROM debug_phase_events
                WHERE oid = '{example_oid}'
                ORDER BY ts NULLS LAST, source
            """
            ).fetchall()
            self.logger.info(
                f"Timeline for example OID with both phases: {example_oid}"
            )
            for r in rows_tl:
                self.logger.info(f"    ts={r[1]}  phase={r[2]}  src={r[3]}")
        else:
            self.logger.info("No example OID found with both phases in events (yet).")
        # === END DEBUG BLOCK ===
        # --- 4) Keep FIRST timestamp per (oid, phase_en) ---
        first_ts = {}  # key=(oid, phase_en) -> ts
        all_phases_en = set()

        for oid, events in events_by_oid.items():
            for phase_en, ts in events:
                if not phase_en or ts is None or pd.isna(ts):
                    continue
                key = (oid, phase_en)
                if key not in first_ts or ts < first_ts[key]:
                    first_ts[key] = ts
                all_phases_en.add(phase_en)

        # --- 5) Build wide rows with English-only start_<phase> columns ---
        start_cols = sorted(f"start_{to_ident(p)}" for p in all_phases_en if p)
        wide_by_oid = {o["Oid"]: {c: None for c in start_cols} for o in opps}

        for (oid, phase_en), ts in first_ts.items():
            col = f"start_{to_ident(phase_en)}"
            if oid in wide_by_oid:
                # store ISO strings for stable writing
                wide_by_oid[oid][col] = (
                    ts.isoformat()
                    if isinstance(ts, pd.Timestamp) and not pd.isna(ts)
                    else None
                )

        # --- 6) Assemble final DataFrame (no German columns) ---
        base_rows = []
        for o in opps:
            rec = {
                "Oid": o["Oid"],
                "ClosingDate": o["ClosingDate"],
                "ExpectedTurnover": o["ExpectedTurnover"],
                "Currency": o["Currency"],
                "Status": o["Status"],
                "TargetProbability": o["TargetProbability"],
                "Phase": (
                    o["Phase_EN"] or o["Phase_DE"]
                ),  # base Phase shown in EN if present
                "Reason": o["Reason"],
                "RequirementsDescription": o["RequirementsDescription"],
                "Subject": o["Subject"],
                "Common_EntityTitle": o["Common_EntityTitle"],
                "Probability": o["Probability"],
            }
            rec.update(wide_by_oid[o["Oid"]])
            base_rows.append(rec)

        df = pd.DataFrame.from_records(base_rows)

        # deterministic order
        base_cols = [
            "Oid",
            "ClosingDate",
            "ExpectedTurnover",
            "Currency",
            "Status",
            "TargetProbability",
            "Phase",
            "Reason",
            "RequirementsDescription",
            "Subject",
            "Common_EntityTitle",
            "Probability",
        ]
        dyn_cols = sorted([c for c in df.columns if c.startswith("start_")])
        df = df.reindex(columns=base_cols + dyn_cols)
        for col in ["ClosingDate"] + dyn_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce", utc=True).dt.date

        # --- 7) Write back to DuckDB (this table will NOT include any german 'start__abschluss_' columns) ---
        self.local_database.con.register("tmp_transformed_df", df)
        self.local_database.con.execute(
            "CREATE OR REPLACE TABLE transformed_opportunity AS SELECT * FROM tmp_transformed_df"
        )
        self.local_database.con.unregister("tmp_transformed_df")

        self.logger.info(
            f"transformed_opportunity written with {len(df)} rows and {len(df.columns)} columns "
            f"({len(dyn_cols)} phase start columns: {', '.join(dyn_cols) if dyn_cols else 'none'})"
        )

        # Optional: export/upload as in your existing pipeline
        if self.cfg.transform.dump_files:
            self.local_database.export_table(
                table_name="transformed_opportunity",
                fh=self.fh,
                step=ETLStep.TRANSFORM,
                entity="Opportunity",
                gzip_enabled=False,
            )

        if self.cfg.transform.load_to_nemo:
            self.local_database.upload_table_to_nemo(
                table_name="transformed_opportunity",
                project_name=f"{self.cfg.transform.nemo_project_prefix}Opportunity",
                delete_temp_files=self.cfg.transform.delete_temp_files,
            )
