var cachedGeojson = null;


const CENTERS = {
    "AI": [-170.2, 52.2],
    "GOA": [-153.26, 57]
};

const SCALES = {
    "AI": 1500,
    "GOA": 900
};

const ROTATIONS = {
    "AI": [1,0],
    "GOA": [-1, -0.3]
}

const BASE_WIDTH = 932;

const TEMPERATURE_RANGE = [0, 18];
const TEMPERATURE_COLORS = [
    '#f1eef6',
    '#d0d1e6',
    '#a6bddb',
    '#74a9cf',
    '#3690c0',
    '#0570b0',
    '#034e7b'
];
const MAX_CPUE = 23300;
const MAX_AREA = 3000;


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

    constructor(element, displaySelection) {
        const self = this;

        self._element = element;
        self._displaySelection = displaySelection;

        const svgElement = self._element.querySelector(".viz");
        self._selection = d3.select("#" + svgElement.id);

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
        const fishLayer2 = self._selection.append("g")
            .classed("fish", true)
            .classed("fish-2", true);
        const fishLayer1 = self._selection.append("g")
            .classed("fish", true)
            .classed("fish-1", true);

        self._redraw();
    }

    _redraw() {
        const self = this;

        const redrawInner = () => {

            const waterLayer = self._selection.select(".water");
            const landLayer = self._selection.select(".land");
            const fishLayer2 = self._selection.select(".fish-2");
            const fishLayer1 = self._selection.select(".fish-1");

            const survey = self._displaySelection.getSurvey();
            const projection = self._buildProjection(survey);

            const temperatureMode = self._displaySelection.getTemperatureMode();
            const selection1 = self._displaySelection.getSpeciesSelection1();
            const selection2 = self._displaySelection.getSpeciesSelection2();

            self._requestLand()
                .then(self._makeFutureRenderLand(landLayer, projection))
                .then(self._makeFutureDataRequest(survey, selection1))
                .then(self._makeFutureInterpretPoints(projection, temperatureMode))
                .then(self._makeFutureRenderWater(waterLayer, projection))
                .then(self._makeFutureRenderFish(fishLayer1, projection))
                .then(self._makeFutureDataRequest(survey, selection2))
                .then(self._makeFutureInterpretPoints(projection, temperatureMode))
                .then(self._makeFutureRenderFish(fishLayer2, projection))
                .then(() => self._hideLoading());
        }

        self._showLoading();
        setTimeout(redrawInner, 500);
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
                        parseFloat(target['lngLow']),
                        parseFloat(target['latLow'])
                    ]);

                    const highPoint = projection([
                        parseFloat(target['lngHigh']),
                        parseFloat(target['latHigh'])
                    ]);

                    const x = lowPoint[0];
                    const y = lowPoint[1];
                    const width = highPoint[0] - lowPoint[0];
                    const height = lowPoint[1] - highPoint[1];

                    const weight = parseFloat(target["weight"]);
                    const area = parseFloat(target["areaSwept"])
                    const cpue = weight / area;

                    const temperature = {
                        "bottom": target["bottomTemperature"],
                        "surface": target["surfaceTemperature"],
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

    _makeFutureRenderWater(waterLayer, projection) {
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

                const waterScale = d3.scaleQuantize()
                    .domain(TEMPERATURE_RANGE)
                    .range(TEMPERATURE_COLORS);

                const rects = waterLayer.selectAll(".grid");
                rects.transition()
                    .attr("x", (datum) => datum.getX())
                    .attr("y", (datum) => datum.getY())
                    .attr("width", (datum) => datum.getWidth())
                    .attr("height", (datum) => datum.getHeight())
                    .attr("fill",(datum) => {
                        const temperature = datum.getTemperature();
                        if (temperature === null) {
                            return "#0570b0";
                        } else {
                            return waterScale(temperature);
                        }
                    });

                resolve(dataset);
            });
        };
    }

    _makeFutureRenderFish(layer, projection) {
        return (dataset) => {
            return new Promise((resolve, reject) => {
                const bound = layer.selectAll(".fish-marker")
                    .data(dataset, (x) => x.getGeohash());

                bound.exit().remove();

                bound.enter()
                    .append("ellipse")
                    .attr("cx", (datum) => datum.getCenterX())
                    .attr("cy", (datum) => datum.getCenterY())
                    .classed("fish-marker", true);

                const areaScale = d3.scaleLinear()
                    .domain([0, MAX_CPUE])
                    .range([0, MAX_AREA]);

                const radiusScale = (x) => Math.sqrt(areaScale(x));

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

    _makeFutureDataRequest(survey, speciesSelection) {
        const self = this;

        return () => {
            return new Promise((resolve, reject) => {
                if (speciesSelection.getName() === "None") {
                    resolve([]);
                    return;
                }

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
                const url = "/geohashes.csv?" + queryString;

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
