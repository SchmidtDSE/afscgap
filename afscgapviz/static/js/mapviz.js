/**
 * Logic for rendering the map and supporting components of the visualization.
 * 
 * @license BSD 3 Clause
 * @author Regents of University of California / The Eric and Wendy Schmidt
 *      Center for Data Science and the Environment at UC Berkeley.
 */

// Geographic centers for the different regions to be used in the projection.
const CENTERS = {
    "AI": [-170.2, 52.2],
    "BSS": [-175.5, 57],
    "EBS": [-177, 58.5],
    "GOA": [-153.26, 57],
    "NBS": [-176, 63]
};

// Recommended scaling factor for different regions to be used in the
// projection.
const SCALES = {
    "AI": 1500,
    "BSS": 1100,
    "EBS": 950,
    "GOA": 900,
    "NBS": 1200
};

// Recommended rotations for the different regions to be used in the projection.
const ROTATIONS = {
    "AI": [1,0],
    "BSS": [-1, -0.3],
    "EBS": [-1, -0.3],
    "GOA": [-1, -0.3],
    "NBS": [-1, -0.3]
}

// Color to use for the square indicating that a haul took place but no
// temperature information to show.
const PRESENCE_INDICATOR_COLOR = "#0570b0";


/**
 * Representation of a single geohash for a single survey / species / year.
 */
class MapDatum {

    /**
     * Create new information about a geohash.
     * 
     * @param {string} geohash The geohash as a string.
     * @param {number} x The x coordinate in visualization pixel space.
     * @param {number} y The y coordinate in visualization pixel space.
     * @param {number} width The width of the geohash in visualization pixel
     *      space.
     * @param {number} height The height of the geohash in visualization pixel
     *      space.
     * @param {number} temperature The temperature in celcius reported for this
     *      geohash given the user's selections.
     * @param {number} cpue The catch per unit effort reported for this geohash
     *      given the user's selections.
     */
    constructor(geohash, x, y, width, height, temperature, cpue) {
        const self = this;

        self._geohash = geohash;
        self._x = x;
        self._y = y;
        self._width = width;
        self._height = height;
        self._temperature = temperature;
        self._cpue = cpue;
    }

    /**
     * Get the geohash string associated with this region.
     * 
     * @return {string} The geohash as a string.
     */
    getGeohash() {
        const self = this;

        return self._geohash;
    }

    /**
     * Get the horizontal pixel coordinate of this region.
     * 
     * @return {number} The x coordinate in visualization pixel space.
     */
    getX() {
        const self = this;

        return self._x;
    }

    /**
     * Get the vertical pixel coordinate of this region.
     * 
     * @return {number} The y coordinate in visualization pixel space.
     */
    getY() {
        const self = this;

        return self._y;
    }

    /**
     * Get the horizontal center pixel coordinate for this region.
     * 
     * @return {number} Get the horiztonal pixel coordinate from which fish
     *      markers should be drawn.
     */
    getCenterX() {
        const self = this;

        return self.getX() + self.getWidth() / 2;
    }

    /**
     * Get the vertical center pixel coordinate for this region.
     * 
     * @return {number} Get the vertical pixel coordinate from which fish
     *      markers should be drawn.
     */
    getCenterY() {
        const self = this;

        return self.getY() + self.getHeight() / 2;
    }

    /**
     * Get the horizontal size of this region in pixels.
     * 
     * @return {number} The width of the geohash in visualization pixel space.
     */
    getWidth() {
        const self = this;

        return self._width;
    }

    /**
     * Get the vertical size of this region in pixels.
     * 
     * @return {number} The height of the geohash in visualization pixel space.
     */
    getHeight() {
        const self = this;

        return self._height;
    }

    /**
     * Get the temperature or temperture change seen in this region.
     * 
     * @return {number} The temperature in celcius reported for this geohash
     *      given the user's selections.
     */
    getTemperature() {
        const self = this;

        return self._temperature;
    }

    /**
     * Get the kg / hectare reported for the speices of interest in this region.
     * 
     * @return {number} The catch per unit effort reported for this geohash
     *      given the user's selections.
     */
    getCpue() {
        const self = this;

        return self._cpue;
    }

}


/**
 * Presenter for the map visualization and its supporting data displays.
 */
class MapViz {

    /**
     * Create a new map visualization presenter.
     * 
     * @param {HTMLElement} element The visualization panel to be controlled
     *      by this presenter.
     * @param {DisplaySelection} displaySelection The current or starting set of
     *      user selections / filters defining the dataset of interest.
     * @param {CommonScale} commonScale The scale builder to use in drawing
     *      this visualization's glyphs.
     * @param {function} onRender Function to call after the map component is
     *      rendered.
     * @param {function} onGeohashEnter Function to call when the user selects
     *      a geohash.
     * @param {function} onGeohashLeave Function to call when the user
     *      un-selects a geohash.
     */
    constructor(element, displaySelection, commonScale, onRender,
        onGeohashEnter, onGeohashLeave) {
        const self = this;

        self._element = element;
        self._displaySelection = displaySelection;
        self._onRender = onRender;

        const svgElement = self._element.querySelector(".viz");
        self._selection = d3.select("#" + svgElement.id);

        d3.select("#" + self._element.id)
            .select(".overall-catch-panel")
            .selectAll(".bar")
            .style("width", "0px");

        self._commonScale = commonScale;

        self._onGeohashEnter = onGeohashEnter;
        self._onGeohashLeave = onGeohashLeave;

        self._cachedTempDataset = null;
        self._cachedFirstDataset = null;
        self._cachedSecondDataset = null;

        self._requestBuild();
    }

    /**
     * Transition this visualization to a new dataset subset.
     * 
     * @param {DisplaySelection} displaySelection New dataset of interest
     *      definition.
     */
    updateSelection(displaySelection) {
        const self = this;

        self._displaySelection = displaySelection;
        self._redraw();
    }

    /**
     * Highlight and provide additional information on a specific geohash.
     * 
     * @param {stirng} geohash The string geohash to highlight.
     */
    selectGeohash(geohash) {
        const self = this;

        const graphDescriptionInner = self._element.querySelector(
            ".graph-description-inner"
        );
        const positionDisplay = self._element.querySelector(
            ".position-hover-display"
        );
        const temperatureDisplay = self._element.querySelector(
            ".temperature-hover-display"
        );
        const species1Display = self._element.querySelector(
            ".species-1-hover-display"
        );
        const species2Display = self._element.querySelector(
            ".species-2-hover-display"
        );

        if (geohash === null) {
            positionDisplay.innerHTML = "";
            temperatureDisplay.innerHTML = "";
            species1Display.innerHTML = "";
            species2Display.innerHTML = "";
            graphDescriptionInner.style.display = "block";
            self._selection.selectAll(".hover-target").style("opacity", 0);
            return;
        }

        graphDescriptionInner.style.display = "none";

        /**
         * Display the name of the geohash highlighted.
         */
        const displayGeohash = () => {
            positionDisplay.innerHTML = "Geohash: " + geohash;
        };

        /**
         * Within the given dataset find the geohash of interest (as provided)
         * by the enclosing variable space.
         * 
         * @param {Array} dataset The dataset of MapDatums to filter.
         * @return {?MapDatum} The first MapDatum corresponding to the geohash
         *      found or null if no data avilable on the geohash of interest.
         */
        const findGeohash = (dataset) => {
            if (dataset === null) {
                return null;
            }
            
            const matching = dataset.filter(
                (x) => x.getGeohash() === geohash
            );
            
            if (matching.length == 0) {
                return null;
            }

            return matching[0];
        };
        
        /**
         * Display information about the geohash's temperature.
         */
        const displayTemperature = () => {
            const matchingRecord = findGeohash(self._cachedTempDataset);

            if (matchingRecord === null) {
                return;
            }

            const secondSelect = self._displaySelection.getSpeciesSelection2();
            const isComparing = secondSelect.getIsActive();
            const prefix = isComparing ? "Change in temperature: " : "Temperature: ";
            const temperature = matchingRecord.getTemperature();
            const roundedTemp = Math.round(temperature * 10) / 10;
            const message = prefix + roundedTemp + " C";
            temperatureDisplay.innerHTML = message;
        };

        /**
         * Display information about a species at the geohash of interest.
         * 
         * Display information about a species at the geohash of interest which
         * comes from the containing scope.
         * 
         * @param {Array} dataset The collection of MapDatums available for the
         *      species of interest.
         * @param {HTMLElement} element The element on which this information
         *      should be displayed.
         * @param {SpeciesSelection} speciesSelection The species / year for
         *      which this information is being provided and that corresopnds
         *      to the given dataset.
         */
        const displaySpecies = (dataset, element, speciesSelection) => {
            const matchingRecord = findGeohash(dataset);

            if (!speciesSelection.getIsActive()) {
                return;
            }

            const speciesDescription = [
                speciesSelection.getName(),
                "(" + speciesSelection.getYear() + ")"
            ].join(" ");

            if (matchingRecord === null) {
                element.innerHTML = speciesDescription + ": Not Surveyed";
                return;
            }

            const cpue = matchingRecord.getCpue();
            const roundedCpue = Math.round(cpue * 100) / 100;
            const cpueStr = roundedCpue + " kg/hectare";
            const message = speciesDescription + ": " + cpueStr;
            element.innerHTML = message;
        };

        displayGeohash();
        if (self._displaySelection.getTemperatureEnabled()) {
            displayTemperature();
        }
        displaySpecies(
            self._cachedFirstDataset,
            species1Display,
            self._displaySelection.getSpeciesSelection1()
        );
        displaySpecies(
            self._cachedSecondDataset,
            species2Display,
            self._displaySelection.getSpeciesSelection2()
        );

        self._selection.selectAll(".hover-target")
            .style("opacity", (x) => x.getGeohash() === geohash ? 1 : 0);
    }

    /**
     * Rebuild the map layers.
     */
    _requestBuild() {
        const self = this;

        self._selection.html("");
        const waterLayer = self._selection.append("g").classed("water", true);
        const negativeLayer = self._selection.append("g")
            .classed("negative-markers", true);
        const landLayer = self._selection.append("g").classed("land", true);
        const fishLayer1 = self._selection.append("g")
            .classed("fish", true)
            .classed("fish-1", true);
        const fishLayer2 = self._selection.append("g")
            .classed("fish", true)
            .classed("fish-2", true);
        const hoverLayer = self._selection.append("g").classed("hover", true);

        self._redraw();
    }

    /**
     * Build and/or transition all map layers to display the currently selected
     * dataset.
     */
    _redraw() {
        const self = this;

        /**
         * Request updated scales from the CommonScale and draw the map.
         */
        const getScaleAndRedraw = () => {
            self._commonScale.getScales().then(redrawInner);
        };

        /**
         * Redraw / transition all map elements.
         */
        const redrawInner = (scales) => {
            const dispSelect = self._displaySelection;
            const selection1 = dispSelect.getSpeciesSelection1();
            const selection2 = dispSelect.getSpeciesSelection2();

            const temperatureMode = dispSelect.getTemperatureMode();
            const isTempDisabled = !dispSelect.getTemperatureEnabled();
            const secondDisabled = !selection2.getIsActive();
            const useComparison = !isTempDisabled && !secondDisabled;

            const radiusScale = scales.getRadiusScale();
            const waterScale = scales.getWaterScale(useComparison);

            const waterLayer = self._selection.select(".water");
            const hoverLayer = self._selection.select(".hover");
            const negativeLayer = self._selection.select(".negative-markers");
            const landLayer = self._selection.select(".land");
            const fishLayer2 = self._selection.select(".fish-2");
            const fishLayer1 = self._selection.select(".fish-1");

            const survey = dispSelect.getSurvey();
            const projection = self._buildProjection(survey);

            const cachedFirstRequestor = self._makeCachedRequestor(
                self._makeFutureDataRequest(survey, selection1)
            );

            let temperatureRequestor = null;;
            if (useComparison) {
                temperatureRequestor = self._makeFutureDataRequest(
                    survey,
                    selection1,
                    selection2
                );
            } else {
                temperatureRequestor = cachedFirstRequestor;
            }

            self._updateLegend(scales);
            self._updateSummary(scales);

            self._requestLand()
                .then(self._makeFutureRenderLand(landLayer, projection))
                .then(temperatureRequestor)
                .then(self._makeFutureInterpretPoints(
                    projection,
                    temperatureMode
                ))
                .then(self._makeFutureRenderWater(
                    waterLayer,
                    negativeLayer,
                    projection,
                    waterScale
                ))
                .then(self._makeFutureAddHoverTargets(hoverLayer, projection))
                .then((dataset) => { self._cachedTempDataset = dataset; })
                .then(cachedFirstRequestor)
                .then(self._makeFutureInterpretPoints(
                    projection,
                    temperatureMode
                ))
                .then(self._makeFutureRenderFish(
                    fishLayer1,
                    projection,
                    radiusScale
                ))
                .then((dataset) => { self._cachedFirstDataset = dataset; })
                .then(self._makeFutureDataRequest(survey, selection2))
                .then(self._makeFutureInterpretPoints(
                    projection,
                    temperatureMode
                ))
                .then(self._makeFutureRenderFish(
                    fishLayer2,
                    projection,
                    radiusScale
                ))
                .then((dataset) => { self._cachedSecondDataset = dataset; })
                .then(() => self._hideLoading())
                .then(() => self._updateTitles())
                .then(() => self._onRender());
        }

        self._showLoading();
        setTimeout(getScaleAndRedraw, 500);
    }

    /**
     * Update the chart description and titles shown to the user.
     */
    _updateTitles() {
        const self = this;

        const hasData = !self._selection.selectAll(".fish-marker").empty();

        /**
         * Indicate that no matching data were found.
         */
        const updateNoData = (hasData) => {
            const target = self._element.querySelector(".no-data-message");
            target.style.display = hasData ? "none": "block";
        };

        /**
         * Create a string describing a species / year selection.
         * 
         * @param {SpeciesSelection} species The selection to summarize.
         * @return {string} Description of the selection.
         */
        const getSpeciesDescription = (species) => {
            const year = "(" + species.getYear() + ")";
            const message = species.getName() + " " + year;
            return message;
        }

        /**
         * Update the title describing the chart shown to the user.
         * 
         * @param hasData {boolean} True if matching data for the current
         *      selection were found and false otherwise.
         */
        const updateTitle = (hasData) => {
            const target = self._element.querySelector(
                ".graph-description-inner"
            );
            const prefix = self._displaySelection.getSurvey() + ": ";
            
            const firstSpecies = self._displaySelection.getSpeciesSelection1();
            const firstMessage = getSpeciesDescription(firstSpecies);

            const secondSpecies = self._displaySelection.getSpeciesSelection2();
            const secondMessage = getSpeciesDescription(secondSpecies);

            const isComparing = secondSpecies.getIsActive();

            const speciesMessages = [firstMessage];
            if (isComparing) {
                speciesMessages.push(secondMessage);
            }
            const speciesMessage = speciesMessages.join(" vs ");

            const temperatureMode = self._displaySelection.getTemperatureMode();
            let temperatureSuffix = ".";
            if (self._displaySelection.getTemperatureEnabled()) {
                let tempDescription = "";
                if (isComparing) {
                    tempDescription = [
                        "change in",
                        temperatureMode,
                        "(" + secondSpecies.getYear(),
                        "-",
                        firstSpecies.getYear() + ")"
                    ].join(" ");
                } else {
                    tempDescription = temperatureMode;
                }

                temperatureSuffix = [
                    " with",
                    tempDescription,
                    "temperatures."
                ].join(" ");
            }

            const fullMessage = prefix + speciesMessage + temperatureSuffix;
            target.textContent = fullMessage;
            target.style.display = hasData ? "block": "none";
        };

        updateNoData(hasData);
        updateTitle(hasData);
    }

    /**
     * Create a closure over a stateful cache for a future data request.
     * 
     * Create a closure over a stateful cache for a future data reques such that
     * repeat requests for data use the cached value and only the first request
     * actually generates HTTP activity.
     * 
     * @param {function} innerRequestor The future to cache.
     */
    _makeCachedRequestor(innerRequestor) {
        const self = this;
        let cachedValue = null;
        return () => {
            return new Promise((resolve, reject) => {
                if (cachedValue !== null) {
                    resolve(cachedValue);
                    return;
                }

                innerRequestor().then((result) => {
                    cachedValue = result;
                    resolve(cachedValue);
                })
            });
        };
    }

    /**
     * Show a loading spinner on the visualization map to the user.
     */
    _showLoading() {
        const self = this;
        self._element.querySelector(".map-loading").style.display = "block";
    }

    /**
     * Hide the loading spinner on the visualization map to the user.
     */
    _hideLoading() {
        const self = this;
        self._element.querySelector(".map-loading").style.display = "none";
    }

    /**
     * Update the summary CPUE display.
     * 
     * @param {Scales} scales The scales for which the display should be built.
     */
    _updateSummary(scales) {
        const self = this;
        
        const summary = scales.getSummary();
        const barScale = scales.getBarScale();

        const panel = d3.select("#" + self._element.id)
            .select(".overall-catch-panel");

        const cpues = summary.getCpues();

        const displaySpecies = (selection, species) => {
            const key = [
                species.getName(),
                species.getYear()
            ].join("/");

            if (!species.getIsActive() || !cpues.has(key)) {
                selection.select(".label").html("");
                selection.select(".bar").transition()
                    .delay(500)
                    .duration(1000)
                    .style("width", "0px");
                return;
            }

            const cpue = cpues.get(key);

            selection.select(".label").html(
                Math.round(cpue * 100) / 100 + " kg/hectare"
            );

            selection.select(".bar").transition()
                .delay(500)
                .duration(1000)
                .style("width", barScale(cpue) + "px");
        };

        const updateTicks = () => {
            const scaleSelection = panel.select(".scale");

            const ticks = [];
            for (let i = 0; i <= 50; i += 1) {
                ticks.push(i);
            }
            
            const bound = scaleSelection.selectAll(".tick")
                .data(ticks, (x) => x);

            bound.exit().remove();

            const groups = bound.enter().append("g")
                .classed("tick", true)
                .attr("transform", "translate(0 10)");

            groups.append("text")
                .html((x) => {
                    if (x % 5 == 0) {
                        return x == 0 ? x + " kg / hectare" : x;
                    } else {
                        return "";
                    }
                });

            groups.append("rect")
                .attr("x", 0)
                .attr("y", 5)
                .attr("width", 1)
                .attr("height", 2)

            const tickSelection = scaleSelection.selectAll(".tick");

            tickSelection.transition()
                .duration(1000)
                .attr("transform", (x) => {
                    return "translate(" + barScale(x) + " 10)";
                });
        };

        const updateDynamicScalingLink = () => {
            const dynamicEnabled = self._commonScale.getDynamicScaling();
            const messageStatus = dynamicEnabled ? "enabled" : "disabled";
            const message = "Dynamic scaling " + messageStatus;
            panel.select(".dynamic-scaling-link").html(message);
        };

        displaySpecies(
            panel.select(".first-overall-catch"),
            self._displaySelection.getSpeciesSelection1()
        );

        displaySpecies(
            panel.select(".second-overall-catch"),
            self._displaySelection.getSpeciesSelection2()
        );

        updateTicks();

        updateDynamicScalingLink();
    }

    /**
     * Update the legends displayed below the map SVG element.
     * 
     * @param {Scales} scales The scales for which a legend should be built.
     */
    _updateLegend(scales) {
        const self = this;

        const dispSelect = self._displaySelection;
        const secondSelection = dispSelect.getSpeciesSelection2();
        const isComparing = secondSelection.getIsActive();
        const temperatureDisplayed = dispSelect.getTemperatureEnabled();

        const legendSelect = d3.select("#" + self._element.id)
            .select(".legend");

        /**
         * Build a legend describing the fish marker size.
         * 
         * @param {d3.select} tableSelect Selection over the table in which the
         *      data should be rendered.
         */
        const buildRadiusLegend = (tableSelect) => {
            const maxCpue = scales.getSummary().getMaxCpue();
            const step = Math.round(maxCpue / 4);
            const values = [0, 1, 2, 3, 4].map((x) => x * step);

            tableSelect.html("");
            
            const rows = tableSelect.selectAll("tr")
                .data(values)
                .enter()
                .append("tr");

            const svgs = rows.append("td").append("svg")
                .attr("width", 30)
                .attr("height", 30)

            const radiusScale = scales.getRadiusScale();
            svgs.append("ellipse")
                .classed("fish-marker", true)
                .classed("fish-1", true)
                .attr("cx", 15)
                .attr("cy", 15)
                .attr("rx", (x) => radiusScale(x))
                .attr("ry", (x) => radiusScale(x));

            rows.append("td").html((x) => x + " kg / hectare");
        };

        /**
         * Build a legend describing the grid colors used.
         * 
         * @param {d3.select} tableSelect Selection over the table in which the
         *      the grid colors legend should be rendered.
         * @param {number} minTemperature The minimum temperature in celcius
         *      that the scale supports.
         * @param {number} maxTemperature The maximum temperature in celcius
         *      that the scale supports.
         * @param {function} waterScale The scale to be used.
         */
        const buildGridLegend = (tableSelect, minTemperature, maxTemperature,
            waterScale) => {
            const spread = maxTemperature - minTemperature;
            const step = Math.round(spread / 3 * 10) / 10;
            const values = spread == 0 ? [0] : [0, 1, 2, 3].map(
                (x) => x * step + minTemperature
            );

            tableSelect.html("");
            
            const rows = tableSelect.selectAll("tr")
                .data(values)
                .enter()
                .append("tr");

            const svgs = rows.append("td").append("svg")
                .attr("width", 30)
                .attr("height", 30)

            svgs.append("rect")
                .classed("grid", true)
                .attr("x", 5)
                .attr("y", 5)
                .attr("width", 20)
                .attr("height", 20)
                .attr("fill", (x) => waterScale(x))
                .attr("opacity", 0.5);

            svgs.append("rect")
                .attr("x", 7)
                .attr("y", 7)
                .attr("width", 16)
                .attr("height", 16)
                .attr("fill", "rgba(0, 0, 0, 0)")
                .attr("stroke-dasharray", "1,1")
                .attr("stroke", "black")
                .attr("stroke-width", (x) => x < 0 ? 1: 0);

            rows.append("td").html((x) => (Math.round(x * 10) / 10) + " C");
        };

        /**
         * Update text for the legend showing if a haul was taken.
         * 
         * Update text for the legend showing if a haul was taken either in a
         * single dataset or in two datasets being compared.
         */
        const updatePresenceText = (target) => {
            if (isComparing) {
                target.html("Area in both surveys.");
            } else {
                target.html("Area surveyed.");
            }
        };

        /**
         * Update the visibility of legends to only display those relevant to
         * the currently requested visualization.
         */
        const updateVisibility = () => {
            let showGridLegend = false;
            let showDivergingLegend = false;
            let showIndicator = false;

            if (temperatureDisplayed) {
                if (isComparing) {
                    showDivergingLegend = true;
                } else {
                    showGridLegend = true;
                }
            } else {
                showIndicator = true;
            }

            legendSelect.select(".grid-legend-holder").style(
                "display",
                showGridLegend ? "block" : "none"
            );
            legendSelect.select(".grid-diverging-legend-holder").style(
                "display",
                showDivergingLegend ? "block" : "none"
            );
            legendSelect.select(".grid-indicator-holder").style(
                "display",
                showIndicator ? "block" : "none"
            );
        };

        const summary = scales.getSummary();
        buildRadiusLegend(legendSelect.select(".radius-legend"));
        buildGridLegend(
            legendSelect.select(".grid-legend"),
            summary.getMinTemperature(),
            summary.getMaxTemperature(),
            scales.getWaterScale(false)
        );
        buildGridLegend(
            legendSelect.select(".grid-diverging-legend"),
            summary.getMinTemperatureDelta(),
            summary.getMaxTemperatureDelta(),
            scales.getWaterScale(true)
        );
        updatePresenceText(legendSelect.select(".presence-description"));
        updateVisibility();
    }

    /**
     * Request the geojson defining the land layer.
     * 
     * @return {Promise} Promise resolving to the parsed geojson.
     */
    _requestLand() {
        return fetch('/static/geojson/clipped.geojson').then((x) => x.json());
    }

    /**
     * Interpret raw data as MapDatums.
     * 
     * @param {d3.projection} projection The projection to use in displaying the
     *      data.
     * @param {string} temperatureMode The type of temperature ("surface" or
     *      "bottom") to be displayed or "disabled" if no temperature should be
     *      displayed.
     * @return {function} Function which takes in a dataset to interpret and
     *      returns that interpreted dataset as an array of MapDatums.
     */
    _makeFutureInterpretPoints(projection, temperatureMode) {
        return (dataset) => {
            const interpreted = dataset.map((target) => {
                const lowPoint = projection([
                    parseFloat(target['lngLowDegrees']),
                    parseFloat(target['latLowDegrees'])
                ]);

                const highPoint = projection([
                    parseFloat(target['lngHighDegrees']),
                    parseFloat(target['latHighDegrees'])
                ]);

                const nativeWidth = highPoint[0] - lowPoint[0];
                const offset = nativeWidth > 10;

                const x = lowPoint[0] + (offset ? 1 : 0);
                const y = lowPoint[1] + (offset ? 1 : 0);
                const width = highPoint[0] - lowPoint[0] - (offset ? 2 : 0);
                const height = lowPoint[1] - highPoint[1] - (offset ? 3 : 0);

                const weight = parseFloat(target["weightKg"]);
                const area = parseFloat(target["areaSweptHectares"])
                const cpue = weight / area;

                const temperature = {
                    "bottom": target["bottomTemperatureC"],
                    "surface": target["surfaceTemperatureC"],
                    "disabled": null
                }[temperatureMode];

                const geohash = target["geohash"];

                return new MapDatum(
                    geohash,
                    x,
                    y,
                    width,
                    height,
                    temperature,
                    cpue
                );
            });

            return interpreted;
        };
    }

    /**
     * Make a future to render the land (shoreline) base layer.
     * 
     * @param {d3.select} landLayer Selection over the layer in which the land
     *      should be drawn.
     * @param {d3.projection} projection The map projection to use in drawing
     *      this layer.
     * @return {function} Function taking parsed geojson and displaying the
     *      results in landLayer using projection.
     */
    _makeFutureRenderLand(landLayer, projection) {
        const self = this;

        return (geojson) => {
            const generator = d3.geoPath().projection(projection);
            
            landLayer.html("");

            const path = landLayer.selectAll("path")
                .data(geojson.features)
                .enter()
                .append("path");

            path.attr("d", generator);

            return geojson;
        };
    }

    /**
     * Build a future for rendering water (temperature / geohash dataset
     * presence) data.
     * 
     * @param {d3.select} waterLayer The layer into which these glyphs should be
     *      drawn.
     * @param {d3.select} negativeLayer The layer into which negative markers
     *      should be drawn. These are markers indicating that there is a
     *      "negative" value like a below zero temperature or decrease in
     *      temperature.
     * @param {d3.projection} projection The map projection in which these
     *      glyphs should be drawn.
     * @param {function} waterScale Scale taking in a temperature value and
     *      returning a color.
     * @return {function} Function taking a dataset to be rendered into
     *      waterLayer and negativeLayer using projection and waterScale.
     */
    _makeFutureRenderWater(waterLayer, negativeLayer, projection, waterScale) {
        const self = this;

        /**
         * Create the tiles indicating areas where there are haul or what
         * temperatures were seen at that region.
         * 
         * @param {Array} dataset Collection of MapDatums to be rendered.
         */
        const buildWaterTiles = (dataset) => {
            const bound = waterLayer.selectAll(".grid")
                .data(dataset, (datum) => datum.getGeohash());

            bound.exit().remove();

            const newRects = bound.enter()
                .append("rect")
                .classed("grid", true)
                .attr("x", (datum) => datum.getX())
                .attr("y", (datum) => datum.getY());

            const rects = waterLayer.selectAll(".grid");

            rects.transition()
                .attr("x", (datum) => datum.getX())
                .attr("y", (datum) => datum.getY())
                .attr("width", (datum) => datum.getWidth())
                .attr("height", (datum) => datum.getHeight())
                .attr("fill", (datum) => {
                    const temperature = datum.getTemperature();
                    if (temperature === null) {
                        return PRESENCE_INDICATOR_COLOR;
                    } else {
                        return waterScale(temperature);
                    }
                })
                .attr("stroke-width", (datum) => {
                    const temperature = datum.getTemperature();
                    return temperature < 0 ? 1 : 0;
                });
        };

        /**
         * Create the tiles indicating areas where there was a negative value
         * such as a below zero C temperature or a temperature decrease.
         * 
         * @param {Array} dataset Collection of MapDatums to be rendered.
         */
        const buildNegativeIndicators = (dataset) => {
            negativeLayer.html("");
            const negativeMarkers = negativeLayer.selectAll(".grid")
                .data(
                    dataset.filter((datum) => datum.getTemperature() < 0),
                    (datum) => datum.getGeohash()
                )
                .enter()
                .append("rect")
                .classed("grid", true)
                .attr("x", (datum) => datum.getX() + 2)
                .attr("y", (datum) => datum.getY() + 2)
                .attr("width", (datum) => datum.getWidth() - 4)
                .attr("height", (datum) => datum.getHeight() - 4)
                .attr("stroke-dasharray", "1,1");
        };

        return (dataset) => {
            buildWaterTiles(dataset);
            buildNegativeIndicators(dataset);
            return dataset;
        };
    }

    /**
     * Create a future for building hover targets to select geohashes.
     * 
     * @param {d3.select} hoverLayer The map layer into which the hover targets
     *      should be rendered.
     * @param {d3.projection} projection The projection to use when rendering
     *      into hoverLayer.
     * @return {function} Function taking in a dataset for which hover targets
     *      should be built and which renders into hoverLayer using projection.
     */
    _makeFutureAddHoverTargets(hoverLayer, projection) {
        const self = this;

        /**
         * Build the hover targets as transparent rects.
         */
        const builTiles = (dataset) => {
            hoverLayer.html("");
            hoverLayer.selectAll(".grid")
                .data(dataset, (datum) => datum.getGeohash())
                .enter()
                .append("rect")
                .classed("grid", true)
                .classed("hover-target", true)
                .attr("x", (datum) => datum.getX())
                .attr("y", (datum) => datum.getY())
                .attr("width", (datum) => datum.getWidth())
                .attr("height", (datum) => datum.getHeight())
                .on("mouseover", (event, datum) => {
                    self._onGeohashEnter(datum.getGeohash());
                })
                .on("mouseout", (event, datum) => {
                    self._onGeohashLeave(datum.getGeohash());
                });
        };

        return (dataset) => {
            builTiles(dataset);
            return dataset;
        };
    }

    /**
     * Make a future which renders fish (CPUE) markers.
     * 
     * @param {d3.select} layer The layer into which the CPUE markers should be
     *      rendered.
     * @param {d3.projection} projection The projection to use when rendering
     *      markers into layer.
     * @param {function} radiusScale Function which takes in CPUE and outputs
     *      radius.
     */
    _makeFutureRenderFish(layer, projection, radiusScale) {
        return (dataset) => {
            const datasetAllowed = dataset.filter(
                (x) => !isNaN(x.getCenterX())
            );

            const bound = layer.selectAll(".fish-marker")
                .data(datasetAllowed, (x) => x.getGeohash());

            bound.exit().remove();

            bound.enter()
                .append("ellipse")
                .attr("cx", (datum) => datum.getCenterX())
                .attr("cy", (datum) => datum.getCenterY())
                .classed("fish-marker", true);

            const markers = layer.selectAll(".fish-marker")
            markers.transition()
                .attr("cx", (datum) => datum.getCenterX())
                .attr("cy", (datum) => datum.getCenterY())
                .attr("rx", (datum) => radiusScale(datum.getCpue()))
                .attr("ry", (datum) => radiusScale(datum.getCpue()));

            return dataset;
        };
    }

    /**
     * Build a projection (d3.geoMercator) to use to display these data.
     * 
     * @param {string} survey The name of the survey for which a projection
     *      needs to be built like GOA.
     * @return {d3.projection} The projection.
     */
    _buildProjection(survey) {
        const self = this;

        const vizElement = self._element.querySelector(".viz");
        const boundingBox = vizElement.getBoundingClientRect();
        const width = boundingBox.width;
        const height = boundingBox.height;

        const projection = d3.geoMercator()
            .center(CENTERS[survey])
            .scale(SCALES[survey])
            .translate([width/2,height/2])
            .clipExtent([[0, 0], [width, height]])
            .rotate(ROTATIONS[survey]);

        return projection;
    }

    /**
     * Make a future which, when called, requests geohash level data.
     * 
     * @param {string} survey The name of the survey for which data are being
     *      requested like GOA.
     * @param {SpeciesSelection} speciesSelection The year / species to be
     *      displayed in this map.
     * @param {?SpeciesSelection} secondSelection Information the second species
     *      to overlay in this map if any.
     */
    _makeFutureDataRequest(survey, speciesSelection, secondSelection) {
        const self = this;

        return () => {
            return new Promise((resolve, reject) => {
                if (!speciesSelection.getIsActive()) {
                    resolve([]);
                    return;
                }

                const isDense = self._commonScale.getIsDense();
                const url = generateDownloadDataUrl(
                    survey,
                    speciesSelection,
                    secondSelection,
                    isDense ? 3 : 4
                );

                Papa.parse(url, {
                    header: true,
                    download: true,
                    complete: function(results) {
                        resolve(results.data);
                    }
                });
            });
        };
    }

}
