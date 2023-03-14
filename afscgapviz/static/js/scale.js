const MAX_AREA_SPARSE = 150;
const MAX_AREA_DENSE = 200;

const POSITIVE_TEMP_COLORS = [
    '#fddbc7',
    '#f4a582',
    '#d6604d'
];

const NEGATIVE_TEMP_COLORS = [
    '#4393c3',
    '#92c5de',
    '#d1e5f0'
];

const SINGLE_TEMP_COLORS = [
    '#0570b0',
    '#3690c0',
    '#74a9cf',
    '#a6bddb',
    '#d0d1e6',
    '#f1eef6'
];


class Summary {

    constructor(minCpue, maxCpue, minTemperature, maxTemperature,
        minTemperatureDelta, maxTemperatureDelta) {
        const self = this;
        self._minCpue = minCpue;
        self._maxCpue = maxCpue;
        self._minTemperature = minTemperature;
        self._maxTemperature = maxTemperature;
        self._minTemperatureDelta = minTemperatureDelta;
        self._maxTemperatureDelta = maxTemperatureDelta;
    }

    getMinCpue() {
        const self = this;
        return self._minCpue;
    }
    
    getMaxCpue() {
        const self = this;
        return self._maxCpue;
    }
    
    getMinTemperature() {
        const self = this;
        return self._minTemperature;
    }
    
    getMaxTemperature() {
        const self = this;
        return self._maxTemperature;
    }

    getMinTemperatureDelta() {
        const self = this;
        return self._minTemperatureDelta;
    }
    
    getMaxTemperatureDelta() {
        const self = this;
        return self._maxTemperatureDelta;
    }

    combine(other) {
        const self = this;

        const isValid = (x) => x !== null && !isNaN(x);
        
        const minCpues = [
            self.getMinCpue(),
            other.getMinCpue()
        ].filter(isValid);
        
        const maxCpues = [
            self.getMaxCpue(),
            other.getMaxCpue()
        ].filter(isValid);
        
        const minTemperatures = [
            self.getMinTemperature(),
            other.getMinTemperature()
        ].filter(isValid);
        
        const maxTemperatures = [
            self.getMaxTemperature(),
            other.getMaxTemperature()
        ].filter(isValid);

        const minTemperatureDeltas = [
            self.getMinTemperatureDelta(),
            other.getMinTemperatureDelta()
        ];
        
        const maxTemperatureDeltas = [
            self.getMaxTemperatureDelta(),
            other.getMaxTemperatureDelta()
        ];

        return new Summary(
            Math.min(...minCpues),
            Math.max(...maxCpues),
            Math.min(...minTemperatures),
            Math.max(...maxTemperatures),
            Math.min(...minTemperatureDeltas),
            Math.max(...maxTemperatureDeltas)
        );
    }

}


class Scales {

    constructor(summary, radiusScale, waterScale, waterDivergingScale) {
        const self = this;
        self._summary = summary;
        self._radiusScale = radiusScale;
        self._waterScale = waterScale;
        self._waterDivergingScale = waterDivergingScale;
    }

    getSummary() {
        const self = this;
        return self._summary;
    }

    getRadiusScale() {
        const self = this;
        return self._radiusScale;
    }
    
    getWaterScale(diverging) {
        const self = this;

        if (diverging) {
            return self._waterDivergingScale;
        } else {
            return self._waterScale;
        }
    }

}


class CommonScale {

    constructor(getGetters) {
        const self = this;

        self._getGetters = getGetters;
        self._cached = null;
        self._cachedKey = null;
    }

    getScales() {
        const self = this;

        const newKey = self._getGetters().map(
            (x) => x().getKey()
        ).join("/");

        if (self._cachedKey === newKey) {
            return new Promise((resolve, reject) => {
                resolve(self._cached);
            });
        }

        return new Promise((resolve, reject) => {
            self._getScaleNoCache().then((scale) => {
                self._cached = scale;
                self._cachedKey = newKey;
                resolve(scale);
            });
        });
    }

    getIsDense() {
        const self = this;

        const getters = self._getGetters();
        const selections = getters.map((x) => x());

        const getTempEnabled = () => {
            const numWithTempEnabled = selections
                .filter((x) => x.getTemperatureMode() !== "disabled")
                .map((x) => 1)
                .reduce((a, b) => a + b, 0);

            const tempDisabled = numWithTempEnabled == 0;

            return !tempDisabled;
        };

        const getComparing = () => {
            const numComparing = selections
                .filter((x) => x.getSpeciesSelection2().getName() !== "None")
                .map((x) => 1)
                .reduce((a, b) => a + b, 0);

            const isComparing = numComparing > 0;

            return isComparing;
        };
        
        return getTempEnabled() || getComparing();
    }

    _getScaleNoCache() {
        const self = this;

        return new Promise((resolve, reject) => {
            const promises = self._getGetters().map(
                (x) => self._getSummary(x)
            );
            Promise.all(promises).then((values) => {
                const combined = values.reduce((a, b) => a.combine(b));

                const isDense = self.getIsDense();
                const maxArea = isDense ? MAX_AREA_DENSE : MAX_AREA_SPARSE;

                const areaScale = d3.scaleLinear()
                    .domain([0, combined.getMaxCpue()])
                    .range([0, maxArea]);

                const radiusScale = (x) => Math.sqrt(areaScale(x));

                const waterScale = d3.scaleQuantize()
                    .domain([
                        combined.getMinTemperature(),
                        combined.getMaxTemperature()
                    ])
                    .range(SINGLE_TEMP_COLORS);

                const negativeWaterScale = d3.scaleQuantize()
                    .domain([
                        Math.min(
                            combined.getMinTemperatureDelta(),
                            -combined.getMaxTemperatureDelta()
                        ),
                        0
                    ])
                    .range(NEGATIVE_TEMP_COLORS);

                const positiveWaterScale = d3.scaleQuantize()
                    .domain([
                        0,
                        Math.max(
                            -combined.getMinTemperatureDelta(),
                            combined.getMaxTemperatureDelta()
                        )
                    ])
                    .range(POSITIVE_TEMP_COLORS);

                const waterDivergingScale = (x) => {
                    if (x < 0) {
                        return negativeWaterScale(x);
                    } else {
                        return positiveWaterScale(x);
                    }
                };

                resolve(new Scales(
                    combined,
                    radiusScale,
                    waterScale,
                    waterDivergingScale
                ));
            });
        });
    }

    _getSummary(getter) {
        const self = this;

        const displaySelection = getter();
        const survey = displaySelection.getSurvey();
        const speciesSelections = [
            displaySelection.getSpeciesSelection1(),
            displaySelection.getSpeciesSelection2()
        ];

        let promises = null;

        const temperatureMode = displaySelection.getTemperatureMode();
        const temperatureDisabled = temperatureMode === "disabled";
        const secondIsNone = speciesSelections[1].getName() === "None";
        const noComparison = temperatureDisabled || secondIsNone;
        if (noComparison) {
            promises = speciesSelections.map((speciesSelection) => {
                if (speciesSelection.getName() === "None") {
                    return new Promise((resolve, reject) => resolve({
                        "cpue": {"min": null, "max": null},
                        "temperature": {"min": null, "max": null}
                    }));
                }

                const year = speciesSelection.getYear();

                const params = [
                    "survey=" + survey,
                    "year=" + speciesSelection.getYear(),
                    "temperature=" + displaySelection.getTemperatureMode(),
                    "geohashSize=" + (self.getIsDense() ? 4 : 5)
                ];

                if (speciesSelection.getIsSciName()) {
                    params.push("species=" + speciesSelection.getName());
                } else {
                    params.push("commonName=" + speciesSelection.getName());
                }

                const queryString = params.join("&");
                const url = "/summarize.json?" + queryString;

                return fetch(url).then((response) => response.json());
            });
        } else {
            const year = speciesSelections[0].getYear();

            const params = [
                "survey=" + survey,
                "year=" + speciesSelections[0].getYear(),
                "otherYear=" + speciesSelections[1].getYear(),
                "temperature=" + displaySelection.getTemperatureMode(),
                "geohashSize=" + (self.getIsDense() ? 4 : 5),
                "comparison=y"
            ];

            const firstName = speciesSelections[0].getName();
            if (speciesSelections[0].getIsSciName()) {
                params.push("species=" + firstName);
            } else {
                params.push("commonName=" + firstName);
            }

            const secondName = speciesSelections[1].getName();
            if (speciesSelections[1].getIsSciName()) {
                params.push("otherSpecies=" + secondName);
            } else {
                params.push("otherCommonName=" + secondName);
            }

            const queryString = params.join("&");
            const url = "/summarize.json?" + queryString;

            promises = [fetch(url).then((response) => response.json())];
        }
        
        return new Promise((resolve, reject) => {
            Promise.all(promises).then((results) => {
                const summaries = results.map((x) => new Summary(
                    x["cpue"]["min"],
                    x["cpue"]["max"],
                    noComparison ? x["temperature"]["min"] : null,
                    noComparison ? x["temperature"]["max"] : null,
                    noComparison ? null : x["temperature"]["min"],
                    noComparison ? null: x["temperature"]["max"]
                ));
                const combined = summaries.reduce((a, b) => a.combine(b));
                resolve(combined);
            });
        });
    }

}