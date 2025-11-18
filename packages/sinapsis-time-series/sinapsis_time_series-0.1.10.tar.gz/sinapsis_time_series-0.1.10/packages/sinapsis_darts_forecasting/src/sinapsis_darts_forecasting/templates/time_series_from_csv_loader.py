# -*- coding: utf-8 -*-

import os
from typing import Literal

from darts import TimeSeries
from pydantic import Field
from sinapsis_core.data_containers.data_packet import DataContainer, TimeSeriesPacket
from sinapsis_core.template_base.base_models import OutputTypes, TemplateAttributes, UIPropertiesMetadata
from sinapsis_core.template_base.template import Template

from sinapsis_darts_forecasting.helpers.tags import Tags
from sinapsis_darts_forecasting.templates.time_series_from_dataframe_loader import FromDataFrameKwargs


class FromCSVKwargs(FromDataFrameKwargs):
    """Defines and validates parameters for creating Darts TimeSeries directly from CSV files.

    Attributes:
        fill_missing_dates (bool | None): If `True`, adds rows for missing timestamps.
            Defaults to `False`.
        freq (str | None): The frequency of the time series (e.g., 'D' for daily, 'H' for hourly).
        fillna_value (float | None): The value to use for filling any missing data points (NaNs).
        static_covariates (pd.Series | pd.DataFrame | None): External data that is constant
            over time for this series.
        metadata (dict | None): A dictionary for storing arbitrary metadata about the time series.
        make_copy (bool): Whether to create a copy of the underlying data. Defaults to `False` and ignored for CSV
            loading.
        path_to_csv (str): The filename or relative path to the CSV file.
    """

    path_to_csv: str
    make_copy: bool = Field(
        default=False, serialization_alias="copy", description="Whether to create a copy of the underlying data."
    )


class TimeSeriesFromCSVLoader(Template):
    """Template for loading time series data from a CSV file into a Time Series Packet.

    Usage example:

    agent:
        name: my_loader_agent
    templates:
    - template_name: InputTemplate
        class_name: InputTemplate
        attributes: {}
    - template_name: TimeSeriesFromCSVLoader
        class_name: TimeSeriesFromCSVLoader
        template_input: InputTemplate
        attributes:
        root_dir: "/root/.cache/sinapsis"
        assign_to: "content"
        loader_params:
            path_to_csv: "sales_data.csv"
            time_col: "Date"
            value_cols: "Revenue"
            freq: "D"
    """

    UIProperties = UIPropertiesMetadata(
        category="Darts",
        output_type=OutputTypes.TIMESERIES,
        tags=[Tags.DARTS, Tags.DATA, Tags.DATAFRAMES, Tags.PANDAS, Tags.TIME_SERIES],
    )

    class AttributesBaseModel(TemplateAttributes):
        """Defines the attributes required for the CSV Loader template.

        Attributes:
            root_dir (str | None): The base directory where the CSV file is located. If provided, it is prepended to
                `path_to_csv`.
            assign_to (Literal): The specific attribute of the `TimeSeriesPacket` where the loaded data will be
                stored (`content`, `past_covariates`, etc.).
            loader_params (FromCSVKwargs): Configuration parameters for reading the CSV file, including column
                mapping and frequency settings.
        """

        root_dir: str | None = None
        assign_to: Literal["content", "past_covariates", "future_covariates", "predictions"]
        loader_params: FromCSVKwargs

    def _load_csv(self, time_series_packet: TimeSeriesPacket) -> TimeSeries:
        """Reads the CSV file and assigns the Darts TimeSeries object to the packet.

        Args:
            time_series_packet (TimeSeriesPacket): The packet to populate with the loaded series.
        """
        if self.attributes.root_dir:
            filepath = os.path.join(self.attributes.root_dir, self.attributes.loader_params.path_to_csv)
        else:
            filepath = self.attributes.loader_params.path_to_csv
        setattr(
            time_series_packet,
            self.attributes.assign_to,
            TimeSeries.from_csv(
                filepath_or_buffer=filepath,
                **self.attributes.loader_params.model_dump(
                    exclude_none=True, exclude={"copy", "path_to_csv"}, by_alias=True
                ),
            ),
        )

    def execute(self, container: DataContainer) -> DataContainer:
        """Executes the template by creating a new packet and loading the CSV data.

        Args:
            container (DataContainer): The input data container.

        Returns:
            DataContainer: The container updated with a new `TimeSeriesPacket` containing
                the loaded CSV data.
        """
        packet = TimeSeriesPacket()
        self._load_csv(packet)
        container.time_series.append(packet)

        return container
