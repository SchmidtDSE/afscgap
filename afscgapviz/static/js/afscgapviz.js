class VizPresenter {

    constructor() {
        const self = this;

        self._displaysLoaded = 0;
        self._resized = false;
        self._intro = null;

        document.getElementById("displays").style.opacity = 0;
        document.getElementById("intro-loading").style.display = "block";
        document.getElementById("intro-links").style.display = "none";

        self._commonScale = new CommonScale(() => {
            return [
                () => self._display1.getSelection(),
                () => self._display2.getSelection()
            ];
        });

        self._display1 = new Display(
            1,
            document.getElementById("display-1"),
            self._commonScale,
            () => self._refreshAllDatasets(),
            () => self._refreshAllSelections(),
            () => self._checkToStartIntro()
        );
        self._display2 = new Display(
            2,
            document.getElementById("display-2"),
            self._commonScale,
            () => self._refreshAllDatasets(),
            () => self._refreshAllSelections(),
            () => self._checkToStartIntro()
        );

        document.getElementById("share-link").addEventListener(
            "click",
            (event) => {
                event.preventDefault();
                navigator.clipboard.writeText(window.location.href);
                alert("Copied sharable URL to clipboard.");
            });

        window.addEventListener("resize", () => { self._resized = true; });
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

        console.log(window.location.href);
        if (window.location.href.indexOf("?state") == -1) {
            document.getElementById("intro-links").style.display = "block";
            self._intro = new Intro();
        } else {
            self._intro = null;
            document.getElementById("tutorial-panel").style.display = "none";
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

}
