class VizPresenter {

    constructor() {
        const self = this;

        self._displaysLoaded = 0;
        self._resized = false;
        self._intro = null;
        self._selectedGeohash = null;

        document.getElementById("displays").style.opacity = 0;
        document.getElementById("intro-loading").style.display = "block";
        document.getElementById("intro-links").style.display = "none";

        self._commonScale = new CommonScale(
            () => {
                return [
                    () => self._display1.getSelection(),
                    () => self._display2.getSelection()
                ];
            },
            () => self._getDynamicScaling()
        );

        self._display1 = new Display(
            1,
            document.getElementById("display-1"),
            self._commonScale,
            () => self._refreshAllDatasets(),
            () => self._refreshAllSelections(),
            () => self._checkToStartIntro(),
            (geohash) => self._onGeohashEnter(geohash),
            (geohash) => self._onGeohashLeave(geohash)
        );
        self._display2 = new Display(
            2,
            document.getElementById("display-2"),
            self._commonScale,
            () => self._refreshAllDatasets(),
            () => self._refreshAllSelections(),
            () => self._checkToStartIntro(),
            (geohash) => self._onGeohashEnter(geohash),
            (geohash) => self._onGeohashLeave(geohash)
        );

        document.getElementById("share-link").addEventListener(
            "click",
            (event) => {
                event.preventDefault();
                navigator.clipboard.writeText(window.location.href);
                alert("Copied sharable URL to clipboard.");
            });

        window.addEventListener("resize", () => { self._resized = true; });

        document.getElementById("dynamic-scales-check").addEventListener(
            "change",
            () => self._refreshAllDatasets()
        );
    }

    _getDynamicScaling() {
        const self = this;

        const checkbox = document.getElementById("dynamic-scales-check");
        return checkbox.checked;
    }

    _refreshAllDatasets() {
        const self = this;

        self._display1.refreshDataset();
        self._display2.refreshDataset();
        self._updateDeeplink();
    }

    _refreshAllSelections() {
        const self = this;

        self._display1.refreshSelection();
        self._display2.refreshSelection();
        self._updateDeeplink();
    }

    _updateDeeplink() {
        const self = this;

        if (disableDeepLink) {
            return;
        }

        const buildSpeciesPayload = (selection) => {
            const isSciName = selection.getIsSciName();
            return {
                "scientificName": selection.getName(),
                "commonName": selection.getName(),
                "year": selection.getYear()
            };
        };

        const buildSelectionPayload = (selection) => {
            const species1 = selection.getSpeciesSelection1();
            const species2 = selection.getSpeciesSelection2();
            const isSciName = species1.getIsSciName();
            const speciesType = isSciName ? "scientific" : "common";
            return {
                "selections": [
                    buildSpeciesPayload(species1),
                    buildSpeciesPayload(species2)
                ],
                "area": selection.getSurvey(),
                "temperature": selection.getTemperatureMode(),
                "speciesType": speciesType
            };
        };

        const selection1 = self._display1.getSelection();
        const selection2 = self._display2.getSelection();

        const payload = {
            "state": [
                buildSelectionPayload(selection1),
                buildSelectionPayload(selection2)
            ]
        };

        const payloadJson = JSON.stringify(payload);
        history.pushState(
            {"state": payloadJson},
            "AFSCGAP Viz",
            "/?state="+payloadJson
        );
    }

    _startIntro() {
        const self = this;

        d3.select("#displays").transition().style("opacity", 1);

        if (window.location.href.indexOf("?state") == -1) {
            document.getElementById("intro-links").style.display = "block";
            self._intro = new Intro();
        } else {
            self._intro = null;
            document.getElementById("tutorial-panel").style.display = "none";
            document.getElementById("dynamic-scales-options").style.opacity = 1;
        }
    }

    _checkToStartIntro() {
        const self = this;

        self._displaysLoaded++;
        const shouldInitIntro = self._displaysLoaded == 2;
        if (shouldInitIntro) {
            self._startIntro();
            return;
        }

        const bothLoaded = self._displaysLoaded % 2 == 0;
        const introDone = self._intro === null || self._intro.isDone();
        if (self._resized && bothLoaded && !introDone) {
            self._intro.forceSync();
            self._resized = false;
        }
    }

    _onGeohashEnter(geohash) {
        const self = this;
        self._selectGeohash(geohash);
    }

    _onGeohashLeave(geohash) {
        const self = this;
        if (geohash === self._selectedGeohash) {
            self._selectGeohash(null);
        }
    }

    _selectGeohash(geohash) {
        const self = this;
        self._selectedGeohash = geohash;
        self._display1.selectGeohash(geohash);
        self._display2.selectGeohash(geohash);
    }

}
