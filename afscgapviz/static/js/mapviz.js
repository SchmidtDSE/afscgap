var cachedGeojson = null;


const CENTERS = {
    "AI": [-170.2, 52.2],
    "BSS": [-178, 58],
    "EBS": [-178, 58.5],
    "GOA": [-153.26, 57],
    "NBS": [-177, 63]
};

const SCALES = {
    "AI": 1500,
    "BSS": 1100,
    "EBS": 950,
    "GOA": 900,
    "NBS": 1200
};

const ROTATIONS = {
    "AI": [1,0],
    "BSS": [-1, -0.3],
    "EBS": [-1, -0.3],
    "GOA": [-1, -0.3],
    "NBS": [-1, -0.3]
}

const BASE_WIDTH = 932;


class MapDatum {

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

    getGeohash() {
        const self = this;

        return self._geohash;
    }

    getX() {
        const self = this;

        return self._x;
    }

    getY() {
        const self = this;

        return self._y;
    }

    getCenterX() {
        const self = this;

        return self.getX() + self.getWidth() / 2;
    }

    getCenterY() {
        const self = this;

        return self.getY() + self.getHeight() / 2;
    }

    getWidth() {
        const self = this;

        return self._width;
    }

    getHeight() {
        const self = this;

        return self._height;
    }

    getTemperature() {
        const self = this;

        return self._temperature;
    }

    getCpue() {
        const self = this;

        return self._cpue;
    }

}


class MapViz {

    constructor(element, displaySelection, commonScale) {
        const self = this;

        self._element = element;
        self._displaySelection = displaySelection;

        const svgElement = self._element.querySelector(".viz");
        self._selection = d3.select("#" + svgElement.id);

        self._commonScale = commonScale;

        self._requestBuild();
    }

    updateSelection(displaySelection) {
        const self = this;

        self._displaySelection = displaySelection;
        self._redraw();
    }

    _requestBuild() {
        const self = this;

        self._selection.html("");
        const waterLayer = self._selection.append("g").classed("water", true);
        const landLayer = self._selection.append("g").classed("land", true);
        const fishLayer1 = self._selection.append("g")
            .classed("fish", true)
            .classed("fish-1", true);
        const fishLayer2 = self._selection.append("g")
            .classed("fish", true)
            .classed("fish-2", true);

        self._redraw();
    }

    _redraw() {
        const self = this;

        const getScaleAndRedraw = () => {
            self._commonScale.getScales().then(redrawInner);
        };

        const redrawInner = (scales) => {
            const selection1 = self._displaySelection.getSpeciesSelection1();
            const selection2 = self._displaySelection.getSpeciesSelection2();

            const temperatureMode = self._displaySelection.getTemperatureMode();
            const isTempDisabled = temperatureMode === "disabled";
            const secondIsNone = selection2.getName() === "None"
            const useComparison = !isTempDisabled && !secondIsNone;

            const radiusScale = scales.getRadiusScale();
            const waterScale = scales.getWaterScale(useComparison);

            const waterLayer = self._selection.select(".water");
            const landLayer = self._selection.select(".land");
            const fishLayer2 = self._selection.select(".fish-2");
            const fishLayer1 = self._selection.select(".fish-1");

            const survey = self._displaySelection.getSurvey();
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

            self._requestLand()
                .then(self._makeFutureRenderLand(landLayer, projection))
                .then(temperatureRequestor)
                .then(self._makeFutureInterpretPoints(projection, temperatureMode))
                .then(self._makeFutureRenderWater(waterLayer, projection, waterScale))
                .then(cachedFirstRequestor)
                .then(self._makeFutureInterpretPoints(projection, temperatureMode))
                .then(self._makeFutureRenderFish(fishLayer1, projection, radiusScale))
                .then(self._makeFutureDataRequest(survey, selection2))
                .then(self._makeFutureInterpretPoints(projection, temperatureMode))
                .then(self._makeFutureRenderFish(fishLayer2, projection, radiusScale))
                .then(() => self._hideLoading())
                .then(() => self._checkNoData())
        }

        self._showLoading();
        setTimeout(getScaleAndRedraw, 500);
    }

    _checkNoData() {
        const self = this;

        const message = self._element.querySelector(".no-data-message");
        if (self._selection.selectAll(".fish-marker").empty()) {
            message.style.display = "block";
        } else {
            message.style.display = "none";
        }
    }

    _makeCachedRequestor(innerRequestor) {
        const self = this;
        var cachedValue = null;
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

    _showLoading() {
        const self = this;
        self._element.querySelector(".map-loading").style.display = "block";
    }

    _hideLoading() {
        const self = this;
        self._element.querySelector(".map-loading").style.display = "none";
    }

    _requestLand() {
        return fetch('/static/geojson/clipped.geojson').then((x) => x.json());
    }

    _makeFutureInterpretPoints(projection, temperatureMode) {
        return (dataset) => {
            return new Promise((resolve, reject) => {
                const interpreted = dataset.map((target) => {
                    const lowPoint = projection([
                        parseFloat(target['lngLowDegrees']),
                        parseFloat(target['latLowDegrees'])
                    ]);

                    const highPoint = projection([
                        parseFloat(target['lngHighDegrees']),
                        parseFloat(target['latHighDegrees'])
                    ]);

                    const x = lowPoint[0];
                    const y = lowPoint[1];
                    const width = highPoint[0] - lowPoint[0];
                    const height = lowPoint[1] - highPoint[1];

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

                resolve(interpreted);
            });
        };
    }

    _makeFutureRenderLand(landLayer, projection) {
        const self = this;

        return (geojson) => {
            return new Promise((resolve, reject) => {
                const generator = d3.geoPath().projection(projection);
                
                landLayer.html("");

                const path = landLayer.selectAll("path")
                    .data(geojson.features)
                    .enter()
                    .append("path");

                path.attr("d", generator);

                resolve(geojson);
            });
        };
    }

    _makeFutureRenderWater(waterLayer, projection, waterScale) {
        const self = this;

        return (dataset) => {
            return new Promise((resolve, reject) => {
                const bound = waterLayer.selectAll(".grid")
                    .data(dataset, (x) => x.getGeohash());

                bound.exit().remove();

                const newRects = bound.enter()
                    .append("rect")
                    .classed("grid", true)
                    .attr("x", (datum) => datum.getX())
                    .attr("y", (datum) => datum.getY());

                const rects = waterLayer.selectAll(".grid");

                const getOffset = (datum) => {
                    const temperature = datum.getTemperature();
                    return temperature < 0 ? 1 : 0;
                };

                rects.transition()
                    .attr("x", (datum) => datum.getX() + getOffset(datum))
                    .attr("y", (datum) => datum.getY() + getOffset(datum))
                    .attr(
                        "width",
                        (datum) => datum.getWidth() - getOffset(datum)
                    )
                    .attr(
                        "height",
                        (datum) => datum.getHeight() - getOffset(datum)
                    )
                    .attr("fill", (datum) => {
                        const temperature = datum.getTemperature();
                        if (temperature === null) {
                            return "#0570b0";
                        } else {
                            return waterScale(temperature);
                        }
                    })
                    .attr("stroke-width", (datum) => {
                        const temperature = datum.getTemperature();
                        return temperature < 0 ? 1 : 0;
                    });

                resolve(dataset);
            });
        };
    }

    _makeFutureRenderFish(layer, projection, radiusScale) {
        return (dataset) => {
            return new Promise((resolve, reject) => {
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
                    .attr("ry", (datum) => radiusScale(datum.getCpue()));;

                resolve(dataset);
            });
        };
    }

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

    _makeFutureDataRequest(survey, speciesSelection, secondSelection) {
        const self = this;

        return () => {
            return new Promise((resolve, reject) => {
                if (speciesSelection.getName() === "None") {
                    resolve([]);
                    return;
                }

                const allTempDisabled = self._commonScale.getTempDisabled();
                const url = generateDownloadDataUrl(
                    survey,
                    speciesSelection,
                    secondSelection,
                    allTempDisabled ? 5 : 4
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


function generateDownloadDataUrl(survey, speciesSelection, secondSelection,
    geohashSize) {
    const params = [
        "survey=" + survey,
        "year=" + speciesSelection.getYear(),
        "geohashSize=" + geohashSize
    ];

    if (speciesSelection.getIsSciName()) {
        params.push("species=" + speciesSelection.getName());
    } else {
        params.push("commonName=" + speciesSelection.getName());
    }

    if (secondSelection !== undefined) {
        params.push("comparison=y");
        params.push("otherYear=" + secondSelection.getYear());

        const secondName = secondSelection.getName();
        if (secondSelection.getIsSciName()) {
            params.push("otherSpecies=" + secondName);
        } else {
            params.push("otherCommonName=" + secondName);
        }
    }

    const queryString = params.join("&");
    const url = "/geohashes.csv?" + queryString;

    return url;
}
