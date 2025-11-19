"""
High level wrapper around the Process dataset.
"""
from __future__ import annotations

from typing import Any
from uuid import uuid4

from ..core.base import TidasEntity
from ..generated.tidas_processes import (
    ProcessDataSetAdministrativeInformationDataEntryBy,
    ProcessDataSetAdministrativeInformationPublicationAndOwnership,
    ProcessDataSetProcessInformationDataSetInformation,
    ProcessDataSetProcessInformationGeography,
    ProcessDataSetProcessInformationMathematicalRelations,
    ProcessDataSetProcessInformationQuantitativeReference,
    ProcessDataSetProcessInformationTechnology,
    ProcessDataSetProcessInformationTime,
    DataSetInformationClassificationInformationCommonClassification,
    ProcessInformationDataSetInformationClassificationInformation,
    ProcessInformationDataSetInformationName,
    Processes,
    ProcessesProcessDataSet,
    ProcessesProcessDataSetAdministrativeInformation,
    ProcessesProcessDataSetProcessInformation,
    ProcessesProcessDataSetModellingAndValidation,
)
from .utils import default_timestamp, ensure_model, ensure_multilang


class TidasProcess(TidasEntity[Processes]):
    schema_name = "tidas_processes.json"

    def __init__(
        self,
        initial_data: dict[str, Any] | Processes | None = None,
        *,
        validate_on_init: bool = False,
    ) -> None:
        super().__init__(Processes, initial_data, validate_on_init=validate_on_init)

    def ensure_defaults(self) -> None:
        dataset = ensure_model(self, "process_data_set", ProcessesProcessDataSet)
        if not getattr(dataset, "xmlns", None):
            dataset.xmlns = "http://lca.jrc.it/ILCD/Process"
        if not getattr(dataset, "xmlns_common", None):
            dataset.xmlns_common = "http://lca.jrc.it/ILCD/Common"
        if not getattr(dataset, "xmlns_xsi", None):
            dataset.xmlns_xsi = "http://www.w3.org/2001/XMLSchema-instance"
        if not getattr(dataset, "version", None):
            dataset.version = "1.1"
        if not getattr(dataset, "locations", None):
            dataset.locations = "../ILCDLocations.xml"
        if not getattr(dataset, "xsi_schema_location", None):
            dataset.xsi_schema_location = "http://lca.jrc.it/ILCD/Process ../../schemas/ILCD_ProcessDataSet.xsd"

        process_info = ensure_model(dataset, "process_information", ProcessesProcessDataSetProcessInformation)
        data_info = ensure_model(
            process_info, "data_set_information", ProcessDataSetProcessInformationDataSetInformation
        )
        if not getattr(data_info, "common_uuid", None):
            data_info.common_uuid = str(uuid4())
        ensure_model(data_info, "name", ProcessInformationDataSetInformationName)
        ensure_model(
            data_info,
            "classification_information",
            ProcessInformationDataSetInformationClassificationInformation,
        )
        classification_info = getattr(data_info, "classification_information", None)
        if classification_info is not None:
            ensure_model(
                classification_info,
                "common_classification",
                DataSetInformationClassificationInformationCommonClassification,
            )
        for field_name in ("common_synonyms", "common_general_comment"):
            ensure_multilang(data_info, field_name)

        ensure_model(
            process_info,
            "quantitative_reference",
            ProcessDataSetProcessInformationQuantitativeReference,
        )
        ensure_model(process_info, "time", ProcessDataSetProcessInformationTime)
        ensure_model(process_info, "geography", ProcessDataSetProcessInformationGeography)
        ensure_model(process_info, "technology", ProcessDataSetProcessInformationTechnology)
        ensure_model(
            process_info,
            "mathematical_relations",
            ProcessDataSetProcessInformationMathematicalRelations,
        )

        admin = ensure_model(dataset, "administrative_information", ProcessesProcessDataSetAdministrativeInformation)
        data_entry = ensure_model(admin, "data_entry_by", ProcessDataSetAdministrativeInformationDataEntryBy)
        if not getattr(data_entry, "common_time_stamp", None):
            data_entry.common_time_stamp = default_timestamp()
        ensure_model(admin, "publication_and_ownership", ProcessDataSetAdministrativeInformationPublicationAndOwnership)

        ensure_model(dataset, "modelling_and_validation", ProcessesProcessDataSetModellingAndValidation)
