"""
High level wrapper for Flow datasets.
"""
from __future__ import annotations

from typing import Any, Mapping, cast
from uuid import uuid4

from ..core.base import TidasEntity
from ..generated.tidas_flows import (
    FlowDataSetAdministrativeInformationDataEntryBy,
    FlowDataSetAdministrativeInformationPublicationAndOwnership,
    FlowDataSetFlowInformationDataSetInformation,
    Flows,
    FlowsFlowDataSet,
    FlowsFlowDataSetAdministrativeInformation,
    FlowsFlowDataSetFlowInformation,
)
from .utils import default_timestamp, ensure_model, ensure_multilang


class TidasFlow(TidasEntity[Flows]):
    schema_name = "tidas_flows.json"

    def __init__(
        self,
        initial_data: dict[str, Any] | Flows | None = None,
        *,
        validate_on_init: bool = False,
    ) -> None:
        super().__init__(Flows, initial_data, validate_on_init=validate_on_init)

    @property
    def flow_data_set(self) -> FlowsFlowDataSet:
        return cast(FlowsFlowDataSet, getattr(self.model, "flow_data_set"))

    @flow_data_set.setter
    def flow_data_set(self, value: FlowsFlowDataSet | Mapping[str, Any]) -> None:
        TidasEntity.__setattr__(self, "flow_data_set", value)

    def ensure_defaults(self) -> None:
        dataset = ensure_model(self, "flow_data_set", FlowsFlowDataSet)
        dataset.xmlns = dataset.xmlns or "http://lca.jrc.it/ILCD/Flow"
        dataset.xmlns_common = dataset.xmlns_common or "http://lca.jrc.it/ILCD/Common"
        dataset.xmlns_ecn = dataset.xmlns_ecn or "http://eplca.jrc.ec.europa.eu/ILCD/Extensions/2018/ECNumber"
        dataset.xmlns_xsi = dataset.xmlns_xsi or "http://www.w3.org/2001/XMLSchema-instance"
        dataset.version = dataset.version or "1.1"
        dataset.locations = dataset.locations or "../ILCDLocations.xml"
        dataset.xsi_schema_location = (
            dataset.xsi_schema_location
            or "http://lca.jrc.it/ILCD/Flow ../../schemas/ILCD_FlowDataSet.xsd"
        )

        flow_info = ensure_model(
            dataset,
            "flow_information",
            FlowsFlowDataSetFlowInformation,
        )
        data_info = ensure_model(
            flow_info,
            "data_set_information",
            FlowDataSetFlowInformationDataSetInformation,
        )
        if not data_info.common_uuid:
            data_info.common_uuid = str(uuid4())
        ensure_multilang(data_info, "common_synonyms")
        ensure_multilang(data_info, "common_general_comment")

        admin = ensure_model(
            dataset,
            "administrative_information",
            FlowsFlowDataSetAdministrativeInformation,
        )
        data_entry = ensure_model(
            admin,
            "data_entry_by",
            FlowDataSetAdministrativeInformationDataEntryBy,
        )
        if not data_entry.common_time_stamp:
            data_entry.common_time_stamp = default_timestamp()
        ensure_model(
            admin,
            "publication_and_ownership",
            FlowDataSetAdministrativeInformationPublicationAndOwnership,
        )
