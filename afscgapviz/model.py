"""Data structures for the backend for afscgapviz.

Data structures for the backend for visualization tools included as part of the
AFSC GAP for Python project. Note that these data structures are internal and
are not expected to leave the visualization server.

(c) 2023 Regents of University of California / The Eric and Wendy Schmidt Center
for Data Science and the Environment at UC Berkeley.

This file is part of afscgap released under the BSD 3-Clause License. See
LICENSE.txt.
"""
import typing


class SimplifiedRecord:
    """Simplified afscgap.model.Record for the app database.

    Smaller version of an afscgap.model.Record which only includes information
    needed for the AFSC GAP visualization web application. Note that this is an
    internal representation and is not expected to leave the visualization web
    application.
    """

    def __init__(self, year: int, survey: str, species: str, common_name: str,
        geohash: str, surface_temperature: float, bottom_temperature: float,
        weight: float, count: float, area_swept: float,
        num_records_aggregated: int):
        """Create a new SimplifiedRecord.

        Args:
            year: The year in which this observation was made or for which it
                was generated.
            survey: Short form survey name like GOA.
            species: The scientific name of the species that this record
                describes like Gadus macrocephalus.
            common_name: The common name of the species that this record
                describes like Pacific cod.
            geohash: String geohash describing where this observation was made.
            surface_temperature: The average surface temperature associated with
                this record in Celcius.
            bottom_temperature: The average bottom temperature associated with
                this record in Celcius.
            weight: The total weight observed for the species in kilograms.
            count: The total number of specimens observed for the species.
            area_swept: The toal area swept in this region in hectares.
            num_records_aggregated: The number of raw records (either real or
                generated) / number of hauls summarized by this record.
        """
        self._year = year
        self._survey = survey
        self._species = species
        self._common_name = common_name
        self._geohash = geohash
        self._surface_temperature = surface_temperature
        self._bottom_temperature = bottom_temperature
        self._weight = weight
        self._count = count
        self._area_swept = area_swept
        self._num_records_aggregated = num_records_aggregated

    def get_year(self) -> int:
        """Get the year associated with this record.

        Returns:
            The year in which this observation was made or for which it was
            generated.
        """
        return self._year

    def get_survey(self) -> str:
        """Get the short survey name associated with this record.

        Returns:
            Short form survey name like GOA.
        """
        return self._survey

    def get_species(self) -> str:
        """Get the scientific name associated with this record.

        Returns:
            The scientific name of the species that this record describes like
            Gadus macrocephalus.
        """
        return self._species

    def get_common_name(self) -> str:
        """Get the common name associated with this record.

        Returns:
            The common name of the species that this record describes like
            Pacific cod.
        """
        return self._common_name

    def get_geohash(self) -> str:
        """Get the geohash associated with this record.

        Returns:
            String geohash describing where this observation was made.
        """
        return self._geohash

    def get_surface_temperature(self) -> float:
        """Get the average surface temperature associated with this record.

        Returns:
            The average surface temperature associated with this record in
            Celcius.
        """
        return self._surface_temperature

    def get_bottom_temperature(self) -> float:
        """Get the average bottom temperature associated with this record.

        Returns:
            The average bottom temperature associated with this record in
            Celcius.
        """
        return self._bottom_temperature

    def get_weight(self) -> float:
        """Get the total weight associated with this record.

        Returns:
            The total weight observed for the species in kilograms.
        """
        return self._weight

    def get_count(self) -> float:
        """Get the specimen count associated with this record.

        Returns:
            The total weight observed for the species in kilograms.
        """
        return self._count

    def get_area_swept(self) -> float:
        """Get the total area swept represented by this record.

        Returns:
            The toal area swept in this region in hectares.
        """
        return self._area_swept

    def get_num_records_aggregated(self) -> int:
        """Get the number of underlying records summarized by this record.

        Returns:
            The number of raw records (either real or generated) / number of
            hauls summarized by this record.
        """
        return self._num_records_aggregated

    def get_weight_by_area(self) -> float:
        """Get the total weight caught per hectare surveyed in this geohash.

        Returns:
            Weight divided by area as kg / hectares.
        """
        return self.get_weight() / self.get_area_swept()

    def get_count_by_area(self) -> float:
        """Get the number of specimens observed per hectare surveyed in geohash.

        Returns:
            Weight divided by area as count / hectares.
        """
        return self.get_count() / self.get_area_swept()

    def get_key(self) -> str:
        """Get a key describing the metadata of this record.

        Returns:
            String that indicates with what other SimplifiedRecords this can be
            combined with. If a string matches, the two records refer to the
            same species and geohash in the same survey year. Otherwise,
            they cannot be combined.
        """
        pieces = [
            self.get_year(),
            self.get_survey(),
            self.get_species(),
            self.get_common_name(),
            self.get_geohash()
        ]
        pieces_str = map(str, pieces)
        return '\t'.join(pieces_str)

    def combine(self, other: 'SimplifiedRecord') -> 'SimplifiedRecord':
        """Combine two SimplifiedRecords of the same key.

        Args:
            other: The other record to combine this record with.

        Raises:
            AssertionError: Raised if this record and other do not have
                compatible keys and so cannot be aggregated together.

        Returns:
            Combined records.
        """
        assert self.get_key() == other.get_key()

        self_count = self.get_num_records_aggregated()
        other_count = other.get_num_records_aggregated()

        surface_temp = self.get_surface_temperature() * self_count
        surface_temp += other.get_surface_temperature() * other_count
        surface_temp = surface_temp / (self_count + other_count)

        bottom_temp = self.get_bottom_temperature() * self_count
        bottom_temp += other.get_bottom_temperature() * other_count
        bottom_temp = bottom_temp / (self_count + other_count)

        return SimplifiedRecord(
            self._year,
            self._survey,
            self._species,
            self._common_name,
            self._geohash,
            surface_temp,
            bottom_temp,
            self.get_weight() + other.get_weight(),
            self.get_count() + other.get_count(),
            self.get_area_swept() + other.get_area_swept(),
            self_count + other_count
        )


class SurveyAvailability:
    """Structure summarizing data available for a specific survey.

    Structure summarizing data available for a specific survey within the
    broader AFSC GAP dataset.
    """

    def __init__(self, survey: str, years: typing.List[int],
        species: typing.List[str], common_names: typing.List[str]):
        """Create a new availability summary.

        Args:
            survey: The name of the survey for which availability is summarized.
                This should be like "GOA" for example.
            years: List of years for which data are available within this
                survey.
            species: List of scientific names found for any year for the given
                survey. Example is Gadus macrocephalus.
            common_names: List of "common names" found for any year for the
                given survey. Example is Pacific cod.
        """
        self._survey = survey
        self._years = years
        self._species = species
        self._common_names = common_names

    def get_survey(self) -> str:
        """Get the name of the survey summarized.

        Returns:
            Short survey name like GOA.
        """
        return self._survey

    def get_years(self) -> typing.List[int]:
        """Get the years for which this survey's data are available.

        Returns:
            List of years for which data are available within this survey.
        """
        return self._years

    def get_species(self) -> typing.List[str]:
        """Get the scientific names found in this survey.

        Returns:
            List of scientific names found for any year for the given survey.
            Example is Gadus macrocephalus.
        """
        return self._species

    def get_common_names(self) -> typing.List[str]:
        """Get the common names found in this survey.

        Returns:
            List of "common names" found for any year for the given survey.
            Example is Pacific cod.
        """
        return self._common_names
