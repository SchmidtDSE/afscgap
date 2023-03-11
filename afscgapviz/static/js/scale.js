const MAX_AREA = 200;


class CommonScale {

    constructor(getGetters) {
        const self = this;

        self._getGetters = getGetters;
        self._cached = null;
        self._cachedKey = null;
    }

    getScale() {
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

    _getScaleNoCache() {
        const self = this;

        return new Promise((resolve, reject) => {
            const promises = self._getGetters().map(
                (x) => self._getScaleForGetter(x)
            );
            Promise.all(promises).then((values) => {
                const maxCpue = Math.max(...values);

                const areaScale = d3.scaleLinear()
                    .domain([0, maxCpue])
                    .range([0, MAX_AREA]);

                const radiusScale = (x) => Math.sqrt(areaScale(x));

                resolve(radiusScale);
            });
        });
    }

    _getScaleForGetter(getter) {
        const self = this;

        const displaySelection = getter();
        const survey = displaySelection.getSurvey();
        const speciesSelections = [
            displaySelection.getSpeciesSelection1(),
            displaySelection.getSpeciesSelection2()
        ];

        const promises = speciesSelections.map((speciesSelection) => {
            if (speciesSelection.getName() === "None") {
                return new Promise((resolve, reject) => resolve({"max": 0}));
            }

            const year = speciesSelection.getYear();

            const params = [
                "survey=" + survey,
                "year=" + speciesSelection.getYear()
            ];

            if (speciesSelection.getIsSciName()) {
                params.push("species=" + speciesSelection.getName());
            } else {
                params.push("commonName=" + speciesSelection.getName());
            }

            const queryString = params.join("&");
            const url = "/summarizeCpue.json?" + queryString;

            return fetch(url).then((response) => response.json());
        });
        
        return new Promise((resolve, reject) => {
            Promise.all(promises).then((results) => {
                const maxValue = Math.max(...results.map((x) => x["max"]));
                resolve(maxValue);
            });
        });
    }

}