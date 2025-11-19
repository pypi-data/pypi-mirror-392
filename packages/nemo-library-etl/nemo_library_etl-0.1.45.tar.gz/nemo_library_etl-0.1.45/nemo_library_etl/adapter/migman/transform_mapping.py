"""
MigMan ETL Transform Module.

This module handles the transformation phase of the MigMan ETL pipeline.
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
    MigManTransform: Main class handling MigMan data transformation.
"""

from collections import defaultdict
import logging
from pathlib import Path
from typing import Union

from nemo_library_etl.adapter._utils.db_handler_local import ETLDuckDBHandler
from nemo_library_etl.adapter._utils.enums import ETLStep
from nemo_library_etl.adapter.migman.config_models_migman import (
    ConfigMigMan,
)
from nemo_library_etl.adapter._utils.file_handler import ETLFileHandler
from nemo_library import NemoLibrary

from nemo_library_etl.adapter.migman.enums import MigManTransformStep
from nemo_library_etl.adapter.migman.migmanutils import MigManUtils
from nemo_library_etl.adapter.migman.model.migman import MigMan


class MigManTransformMapping:
    """
    Handles transformation of extracted MigMan data.

    This class manages the transformation phase of the MigMan ETL pipeline,
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
        cfg (PipelineMigMan): Pipeline configuration with transformation settings.
    """

    def __init__(
        self,
        nl: NemoLibrary,
        cfg: ConfigMigMan,
        logger: Union[logging.Logger, object],
        fh: ETLFileHandler,
        local_database: ETLDuckDBHandler,
    ) -> None:
        """
        Initialize the MigMan Transform instance.

        Sets up the transformer with the necessary library instances, configuration,
        and logging capabilities for the transformation process.

        Args:
            nl (NemoLibrary): Core Nemo library instance for system integration.
            cfg (PipelineMigMan): Pipeline configuration object containing
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

    def mappings(self) -> None:
        """
        Apply mappings to the MigMan data.

        This method processes the MigMan data by applying predefined mappings
        to transform the data according to business rules and requirements.
        It ensures that the data is correctly formatted and enriched for
        subsequent loading into the target system.

        Note:
            The actual mapping logic needs to be implemented based on
            the specific MigMan system requirements and mapping definitions.
        """
        self.logger.info("Applying mappings to MigMan data")

        if not self.cfg.transform.mapping.active:
            self.logger.info("Mapping configuration is inactive, skipping mappings")
            return

        active_mappings = [m for m in self.cfg.transform.mapping.mappings if m.active]
        if not active_mappings:
            self.logger.info(
                "No active mappings found in configuration, skipping mappings"
            )
            return

        migmandb = MigManUtils.MigManDatabaseLoad()
        self._ingest_mapping_files(active_mappings)
        mapping_details = self._resolve_synonym_fields(migmandb, active_mappings)
        self._apply_mappings(migmandb, mapping_details)

    def _ingest_mapping_files(self, active_mappings: list) -> None:

        for mapping in active_mappings:

            self.logger.info(f"Processing mapping: {mapping.field_name}")

            # ingest mapping file
            mapping_file = (
                Path(self.cfg.etl_directory)
                / "mapping"
                / f"{MigManUtils.slugify_filename(mapping.field_name)}.csv"
            )
            if not mapping_file.exists():
                raise FileNotFoundError(
                    f"Mapping file '{mapping_file}' does not exist for mapping {mapping.field_name}"
                )
            self.logger.info(f"Loading mapping file: {mapping_file.absolute()}")
            self.local_database.ingest_csv(
                filename=mapping_file,
                table_name=f"{MigManTransformStep.MAPPINGS.value}_{MigManUtils.slugify_filename(mapping.field_name)}",
                create_mode="replace",
                header=True,
                quote='"',
                separator=";",
                encoding="utf-8",
            )

    def _resolve_synonym_fields(
        self, migmandb: list[MigMan], active_mappings: list
    ) -> dict:
        mappings = defaultdict(list)
        for mapping in active_mappings:

            # is there a synonym field
            synonym_fields = next(
                (
                    syn.synonym_fields
                    for syn in self.cfg.transform.mapping.synonyms
                    if syn.source_field == mapping.field_name
                ),
                [],
            )
            if not mapping.field_name in synonym_fields:
                synonym_fields.append(mapping.field_name)

            # search for fields to map
            fields = {
                p.project: p
                for p in migmandb
                if p.desc_section_location_in_proalpha in synonym_fields
                and p.project in self.cfg.setup.projects
            }

            for project, value in fields.items():
                mappings[project].append(value)

        return mappings

    def _apply_mappings(
        self,
        migmandb: list[MigMan],
        mapping_details: dict,
    ) -> None:

        for project, mapped_fields in mapping_details.items():
            self.logger.info(f"Applying mappings for project: {project}")

            self.logger.info(f"Mapped fields for project {project}: {mapped_fields}")
            last_transform_table = self.local_database.latest_table_name(
                steps=MigManTransformStep,
                maxstep=MigManTransformStep.MAPPINGS,
                entity=project,
            )
            if last_transform_table is None:
                raise ValueError(f"No table found for entity {project}")

            new_transform_table = f"{MigManTransformStep.MAPPINGS.value}_{MigManUtils.slugify_filename(project)}"

            fields_in_duckdb = self.local_database
            fields_to_map = [
                field.desc_section_location_in_proalpha for field in mapped_fields
            ]

            columns = self.local_database.con.execute(
                f"SELECT name FROM pragma_table_info('{last_transform_table}')"
            ).fetchall()
            fields_in_duckdb = [col[0] for col in columns]

            # unmapped fields remain the same, mapped fields get _orig suffix
            field_selections = [
                f'"{field}" AS "{field}"'
                for field in fields_in_duckdb
                if not field in fields_to_map
            ]
            field_selections += [
                f'"{field}" AS "Orig_{field}"'
                for field in fields_in_duckdb
                if field in fields_to_map
            ]
            
            # add mapped fields
            field_selections += [
                f'COALESCE(map_{MigManUtils.slugify_filename(field.desc_section_location_in_proalpha)}.target_value,"{field.desc_section_location_in_proalpha}") AS "{field.desc_section_location_in_proalpha}"'
                for field in mapped_fields
                if field.desc_section_location_in_proalpha in fields_to_map                
            ]

            # add joins for mapped fields
            join_clauses = []
            for field in mapped_fields:
                mapping_table = f"{MigManTransformStep.MAPPINGS.value}_{MigManUtils.slugify_filename(field.desc_section_location_in_proalpha)}"
                join_clause = f"""LEFT JOIN "{mapping_table}" AS map_{MigManUtils.slugify_filename(field.desc_section_location_in_proalpha)} 
\tON "{last_transform_table}"."{field.desc_section_location_in_proalpha}" = map_{MigManUtils.slugify_filename(field.desc_section_location_in_proalpha)}.source_value """
                join_clauses.append(join_clause)

            # add mapped fields
            
            query = f"""CREATE OR REPLACE TABLE "{new_transform_table}" AS
SELECT 
\t  {"\n\t, ".join(field_selections)}
FROM "{last_transform_table}"
{"\n".join(join_clauses)}
            """

            self.logger.info(
                f"Executing query to fetch data for project {project}: {query}"
            )
            self.local_database.con.execute(query)

            if self.cfg.transform.dump_files:
                self.local_database.export_table(
                    table_name=new_transform_table,
                    fh=self.fh,
                    step=ETLStep.TRANSFORM,
                    entity=project,
                    substep=MigManTransformStep.MAPPINGS,
                )

            if self.cfg.transform.load_to_nemo:
                self.local_database.upload_table_to_nemo(
                    table_name=new_transform_table,
                    project_name=f"{self.cfg.transform.nemo_project_prefix}{project}",
                    delete_temp_files=self.cfg.transform.delete_temp_files,
                )
