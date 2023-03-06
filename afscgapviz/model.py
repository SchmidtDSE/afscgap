class SimplifiedRecord:

    def __init__(self, year: int, survey: str, species: str, common_name: str,
        geohash: str, surface_temperature: float, bottom_temperature: float,
        weight: float, count: float, area_swept: float,
        num_records_aggregated: int):
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
        return self._year

    def get_survey(self) -> str:
        return self._survey

    def get_species(self) -> str:
        return self._species

    def get_common_name(self) -> str:
        return self._common_name

    def get_geohash(self) -> str:
        return self._geohash

    def get_surface_temperature(self) -> float:
        return self._surface_temperature

    def get_bottom_temperature(self) -> float:
        return self._bottom_temperature

    def get_weight(self) -> float:
        return self._weight

    def get_count(self) -> float:
        return self._count

    def get_area_swept(self) -> float:
        return self._area_swept

    def get_num_records_aggregated(self) -> int:
        return self._num_records_aggregated

    def get_weight_by_area(self) -> float:
        return self.get_weight() / self.get_area_swept()

    def get_count_by_area(self) -> float:
        return self.get_count() / self.get_area_swept()

    def get_key(self) -> str:
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
