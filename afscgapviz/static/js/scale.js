const MAX_AREA_NO_TEMP = 150;
const MAX_AREA_TEMP = 200;

const NEGATIVE_TEMP_COLORS = [
    '#de2d26',
    '#fc9272',
    '#fee0d2'
];

const POSITIVE_TEMP_COLORS = [
    '#deebf7',
    '#9ecae1',
    '#3182bd'
];

const SINGLE_TEMP_COLORS = [
    '#f1eef6',
    '#d0d1e6',
    '#a6bddb',
    '#74a9cf',
    '#3690c0',
    '#0570b0',
    '#034e7b'
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

    constructor(radiusScale, waterScale, waterDivergingScale) {
        const self = this;
        self._radiusScale = radiusScale;
        self._waterScale = waterScale;
        self._waterDivergingScale = waterDivergingScale;
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

    getTempDisabled() {
        const self = this;

        const getters = self._getGetters();
        const selections = getters.map((x) => x());

        const numWithTempEnabled = selections
            .filter((x) => x.getTemperatureMode() !== "disabled")
            .map((x) => 1)
            .reduce((a, b) => a + b, 0);

        const tempDisabled = numWithTempEnabled == 0;

        return tempDisabled;
    }

    _getScaleNoCache() {
        const self = this;

        return new Promise((resolve, reject) => {
            const promises = self._getGetters().map(
                (x) => self._getSummary(x)
            );
            Promise.all(promises).then((values) => {
                const combined = values.reduce((a, b) => a.combine(b));

                const tempDisabled = self.getTempDisabled();
                const maxArea = tempDisabled ? MAX_AREA_NO_TEMP : MAX_AREA_TEMP;

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
                        combined.getMinTemperatureDelta(),
                        0
                    ])
                    .range(NEGATIVE_TEMP_COLORS);

                const positiveWaterScale = d3.scaleQuantize()
                    .domain([
                        0,
                        combined.getMaxTemperatureDelta()
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
                    "geohashSize=" + (self.getTempDisabled() ? 5 : 4)
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
                "geohashSize=" + (self.getTempDisabled() ? 5 : 4),
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
                console.log(noComparison, results[0]["temperature"]);
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