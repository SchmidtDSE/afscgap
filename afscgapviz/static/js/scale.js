/**
 * Logic for coordianting scales across visualization components.
 * 
 * Logic which allows the visualization to use the same scales like for color
 * and radius across different displays.
 * 
 * @license BSD 3 Clause
 * @author Regents of University of California / The Eric and Wendy Schmidt
 *      Center for Data Science and the Environment at UC Berkeley.
 */

// The maximum circle area when the map is not too crowded.
const MAX_AREA_SPARSE = 150;

// The maximum circle area when the map is crowded.
const MAX_AREA_DENSE = 200;

// Colors from ColorBrewer for an increase in temperature.
const POSITIVE_TEMP_COLORS = [
    '#fddbc7',
    '#f4a582',
    '#d6604d'
];

// Colors from ColorBrewer for a decrease in temperature.
const NEGATIVE_TEMP_COLORS = [
    '#4393c3',
    '#92c5de',
    '#d1e5f0'
];

// Colors from ColorBrewer for a linear scale of temperature.
const SINGLE_TEMP_COLORS = [
    '#0570b0',
    '#3690c0',
    '#74a9cf',
    '#a6bddb',
    '#d0d1e6',
    '#f1eef6'
];


/**
 * Summary statistics needed for building scales.
 * 
 * Record describing select summary statistics for the user's currently selected
 * data as required for building appropriate scales. This enables the dynamic
 * scales feature which adjusts min and max values as the dataset changes.
 */
class Summary {

    /**
     * Create a new summary of a dataset or a dataset subset.
     * 
     * @param {number} minCpue The smallest observed catch per unit effort in
     *      the dataset subset (in kg / hectare).
     * @param {number} minCpue The largest observed catch per unit effort in the
     *      dataset subset (in kg / hectare).
     * @param {?number} minTemperature The smallest observed temperature in the
     *      dataset subset (in C) or null if no temperatures reported.
     * @param {?number} maxTemperature The largest observed temperature in the
     *      dataset subset (in C) or null if no temperatures reported.
     * @param {?number} minTemperatureDelta The smallest change in temperature
     *      observed in the dataset subset (in C) or null if no temperature
     *      changes reported.
     * @param {?number} maxTemperatureDelta The largest change in temperature
     *      observed in the dataset subset (in C) or null if no temperature
     *      changes reported.
     * @param {Map} cpues CPUEs by "species/year" strings.
     */
    constructor(minCpue, maxCpue, minTemperature, maxTemperature,
        minTemperatureDelta, maxTemperatureDelta, cpues) {
        const self = this;
        self._minCpue = minCpue;
        self._maxCpue = maxCpue;
        self._minTemperature = minTemperature;
        self._maxTemperature = maxTemperature;
        self._minTemperatureDelta = minTemperatureDelta;
        self._maxTemperatureDelta = maxTemperatureDelta;
        self._cpues = cpues;
    }

    /**
     * Get the minimum CPUE observed.
     * 
     * @return {number} The smallest observed catch per unit effort in the
     *      dataset subset (in kg / hectare).
     */
    getMinCpue() {
        const self = this;
        return self._minCpue;
    }
    
    /**
     * Get the maximum CPUE observed.
     * 
     * @return {number} The largest observed catch per unit effort in the
     *      dataset subset (in kg / hectare).
     */
    getMaxCpue() {
        const self = this;
        return self._maxCpue;
    }
    
    /**
     * Get the minimum temperature observed in the dataset.
     * 
     * @return {?number} The smallest observed temperature in the dataset subset
     *      (in C) or null if no temperatures reported.
     */
    getMinTemperature() {
        const self = this;
        return self._minTemperature;
    }
    
    /**
     * Get the maximum temperature observed in the dataset.
     * 
     * @return {?number} The largest observed temperature in the dataset subset
     *      (in C) or null if no temperatures reported.
     */
    getMaxTemperature() {
        const self = this;
        return self._maxTemperature;
    }

    /**
     * Get the minimum change in temperature observed in the dataset.
     * 
     * @return {?number} The smallest change in temperature observed in the
     *      dataset subset (in C) or null if no temperature changes reported.
     */
    getMinTemperatureDelta() {
        const self = this;
        return self._minTemperatureDelta;
    }
    
    /**
     * Get the maximum change in temperature observed in the dataset.
     * 
     * @return {?number} The largest change in temperature observed in the
     *      dataset subset (in C) or null if no temperature changes reported.
     */
    getMaxTemperatureDelta() {
        const self = this;
        return self._maxTemperatureDelta;
    }

    /**
     * Get the CPUEs observed by species/year.
     * 
     * @return {Map} Map whose keys is the species name followed by a forward
     *      slash followed by the four digit year.
     */
    getCpues() {
        const self = this;
        return self._cpues;
    }

    /**
     * Combine this summary with another, aggregating their statistics.
     * 
     * @param {Summary} other The other summary to be combined with this one.
     * @return {Summary} Newly created summary that represents the aggregation
     *      of other and this.
     */
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

        const combinedMap = new Map();
        self.getCpues().forEach((value, key) => {
            combinedMap.set(key, value);
        });
        other.getCpues().forEach((value, key) => {
            combinedMap.set(key, value);
        });

        return new Summary(
            Math.min(...minCpues),
            Math.max(...maxCpues),
            Math.min(...minTemperatures),
            Math.max(...maxTemperatures),
            Math.min(...minTemperatureDeltas),
            Math.max(...maxTemperatureDeltas),
            combinedMap
        );
    }

}


/**
 * Set of scales to use in rendering a visualization.
 */
class Scales {

    /**
     * Create a new set of scales.
     * 
     * @param {Summary} summary 
     * @param {function} radiusScale Function to call in rendering catch data
     *      which takes in the CPUE and outputs the radius for a ellipse marker.
     * @param {function} waterScale Function to call in rendering temperature
     *      data which takes in the temperature and outputs a color.
     * @param {function} waterDivergingScale Function to call in rendering
     *      changes in temperature which takes in the temperature and outputs a
     *      color.
     * @param {function} barScale The scale to use for the summary stats bar
     *      chart.
     */
    constructor(summary, radiusScale, waterScale, waterDivergingScale,
        barScale) {
        const self = this;
        self._summary = summary;
        self._radiusScale = radiusScale;
        self._waterScale = waterScale;
        self._waterDivergingScale = waterDivergingScale;
        self._barScale = barScale;
    }

    /**
     * Get the summary used in building these scales.
     * 
     * @return {Summary} The summary from which these scales were built.
     */
    getSummary() {
        const self = this;
        return self._summary;
    }

    /**
     * Get the scale to use when drawing fish markers.
     * 
     * @return {function} Function to call in rendering catch data which takes
     *      in the CPUE and outputs the radius for a ellipse marker.
     */
    getRadiusScale() {
        const self = this;
        return self._radiusScale;
    }
    
    /**
     * Get the scale to use when drawing water grid.
     * 
     * @param {boolean} diverging Flag indicating if deltas or temperatures are
     *      to be drawn. Pass true for changes in temperature and false
     *      otherwise.
     * @return {function} Scale to use either for displaying temperature or
     *      temperature changes taking in a temperature / delta and outputting
     *      a color.
     */
    getWaterScale(diverging) {
        const self = this;

        if (diverging) {
            return self._waterDivergingScale;
        } else {
            return self._waterScale;
        }
    }

    /**
     * Get the scale to use for the summary metrics display.
     * 
     * @return {function} Function taking total CPUE and returning width in
     *      pixels
     */
    getBarScale() {
        const self = this;
        return self._barScale;
    }

}


/**
 * Utility to generate scales based on current selections in the dataset.
 * 
 * Utility driving the "dynamic scale" feature which generates scales for use
 * across the visualization based on the user's current selections and dataset.
 */
class CommonScale {

    /**
     * Create a new common scale.
     * 
     * @param {function} getGetters Function which return current "getter"
     *      functions for the active Displays on the page. The getters, when
     *      called, provide the DisplaySelections currently active in the
     *      visualization.
     * @param {function} getDynamicScaling Function to call which returns true
     *      if the user has enabled dynamic scaling and false if they have
     *      disabled it.
     */
    constructor(getGetters, getDynamicScaling) {
        const self = this;

        self._getGetters = getGetters;
        self.getDynamicScaling = getDynamicScaling;
        self._cached = null;
        self._cachedKey = null;
    }

    /**
     * Build scales given the current user selections.
     * 
     * Build scales given the current user selections, using cached scales if
     * the selection remains unchanged from the previous call.
     * 
     * @return {Scales} A set of scales appropriate for the current data
     *      selection if dynamic scaling was enabled or a static set of scales
     *      otherwise.
     */
    getScales() {
        const self = this;

        const newKey = self._getGetters().map(
            (x) => x().getKey()
        ).join("/") + "/" + self.getDynamicScaling();

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

    /**
     * Determine if the visualization is likely to be visually dense.
     * 
     * @return {boolean} True if it is likely that glyphs will appear close
     *      together such that visibility adjustments should be made for
     *      readability. False otherwise.
     */
    getIsDense() {
        const self = this;

        const getters = self._getGetters();
        const selections = getters.map((x) => x());

        /**
         * Determine if any display has temperature enabled across the
         * visualization.
         * 
         * @return {boolean} False if all displays have temperature disabled.
         *      True otherwise.
         */
        const getTempEnabled = () => {
            const numWithTempEnabled = selections
                .filter((x) => x.getTemperatureEnabled())
                .map((x) => 1)
                .reduce((a, b) => a + b, 0);

            const tempDisabled = numWithTempEnabled == 0;

            return !tempDisabled;
        };

        /**
         * Determine if any display has multiple species or years selected
         * across the visualization.
         * 
         * @return {boolean} False if all displays only display one year or
         *      species in their map. True otherwise.
         */
        const getComparing = () => {
            const numComparing = selections
                .filter((x) => x.getSpeciesSelection2().getIsActive())
                .map((x) => 1)
                .reduce((a, b) => a + b, 0);

            const isComparing = numComparing > 0;

            return isComparing;
        };
        
        return getTempEnabled() || getComparing();
    }

    /**
     * Rebuild the scales using current selections.
     */
    _getScaleNoCache() {
        const self = this;

        return new Promise((resolve, reject) => {
            let promises = null;

            const innerPromises = promises = self._getGetters().map(
                (x) => self._getSummary(x)
            );

            if (self.getDynamicScaling()) {
                promises = innerPromises;
            } else {
                const outerPromise = new Promise((resolve, reject) => {
                    Promise.all(innerPromises).then((values) => {
                        const value = values.reduce((a, b) => a.combine(b));
                        const summary = new Summary(
                            0,
                            1000,
                            -2,
                            14,
                            -5,
                            5,
                            value.getCpues()
                        );
                        resolve(summary);
                    });
                });
                promises = [outerPromise];
            }

            Promise.all(promises).then((values) => {
                const combined = values.reduce((a, b) => a.combine(b));

                const isDense = self.getIsDense() || self.getDynamicScaling();
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

                const barWidth = document.querySelector(".overall-catch-panel")
                    .getBoundingClientRect()
                    .width;

                let maxCpueOverall = 0;
                if (self.getDynamicScaling()) {
                    combined.getCpues().forEach((value, key) => {
                        maxCpueOverall = Math.max(value, maxCpueOverall);
                    });
                    maxCpueOverall = Math.floor(maxCpueOverall / 5) * 5 + 5;
                } else {
                    maxCpueOverall = 50;
                }

                const barScale = d3.scaleLinear()
                    .domain([0, maxCpueOverall])
                    .range([0, barWidth]);

                resolve(new Scales(
                    combined,
                    radiusScale,
                    waterScale,
                    waterDivergingScale,
                    barScale
                ));
            });
        });
    }

    /**
     * Create a set of summary statistics across the entire dataset.
     * 
     * Create a set of summary statistics across the entire dataset as required
     * for building the scales.
     * 
     * @return {Summary} Newly built summarygetMaxCpue.
     */
    _getSummary(getter) {
        const self = this;

        const displaySelection = getter();
        const speciesSelections = [
            displaySelection.getSpeciesSelection1(),
            displaySelection.getSpeciesSelection2()
        ];

        let promises = null;

        const temperatureDisabled = !displaySelection.getTemperatureEnabled();
        const secondInactive = !speciesSelections[1].getIsActive();
        const noComparison = temperatureDisabled || secondInactive;
        if (noComparison) {
            promises = speciesSelections.map((speciesSelection) => {
                if (!speciesSelection.getIsActive()) {
                    return new Promise((resolve, reject) => resolve({
                        "cpue": {"min": null, "max": null},
                        "temperature": {"min": null, "max": null}
                    }));
                }

                const url = generateSummarizeUrl(
                    displaySelection,
                    speciesSelection,
                    self.getIsDense() ? 3 : 4
                );

                return fetch(url).then((response) => response.json());
            });
        } else {
            const urlFirst = generateSummarizeUrl(
                displaySelection,
                speciesSelections[0],
                self.getIsDense() ? 3 : 4
            );

            const urlSecond = generateSummarizeUrl(
                displaySelection,
                speciesSelections[1],
                self.getIsDense() ? 3 : 4
            );

            const urlCombine = generateSummarizeUrl(
                displaySelection,
                speciesSelections[0],
                self.getIsDense() ? 3 : 4,
                speciesSelections[1]
            );

            const urls = [urlFirst, urlSecond, urlCombine];

            promises = urls.map(
                (x) => fetch(x).then((response) => response.json())
            );
        }
        
        return new Promise((resolve, reject) => {
            Promise.all(promises).then((results) => {
                const summaries = results.map((x) => {
                    let minGlobalCpue = x["cpue"]["min"];
                    let maxGlobalCpue = x["cpue"]["max"];
                    const cpues = new Map();

                    if (x["cpue"]["first"] !== undefined) {
                        minGlobalCpue = Math.min(
                            x["cpue"]["first"]["value"],
                            minGlobalCpue
                        );

                        maxGlobalCpue = Math.max(
                            x["cpue"]["first"]["value"],
                            maxGlobalCpue
                        );

                        const firstKey = [
                            x["cpue"]["first"]["name"],
                            x["cpue"]["first"]["year"]
                        ].join("/");
                        cpues.set(firstKey, x["cpue"]["first"]["value"]);
                    }

                    if (x["cpue"]["second"] !== undefined) {
                        minGlobalCpue = Math.min(
                            x["cpue"]["second"]["value"],
                            minGlobalCpue
                        );

                        maxGlobalCpue = Math.max(
                            x["cpue"]["second"]["value"],
                            maxGlobalCpue
                        );

                        const secondKey = [
                            x["cpue"]["second"]["name"],
                            x["cpue"]["second"]["year"]
                        ].join("/");
                        cpues.set(secondKey, x["cpue"]["second"]["value"]);
                    }

                    const summary = new Summary(
                        minGlobalCpue,
                        maxGlobalCpue,
                        noComparison ? x["temperature"]["min"] : null,
                        noComparison ? x["temperature"]["max"] : null,
                        noComparison ? null : x["temperature"]["min"],
                        noComparison ? null: x["temperature"]["max"],
                        cpues
                    );

                    return summary;
                });
                const combined = summaries.reduce((a, b) => a.combine(b));
                resolve(combined);
            });
        });
    }

}