/**
 * Main entrypoint for the AFSC GAP visualization tool.
 * 
 * Main entrypoint for the AFSC GAP visualization tool included as part of the
 * Python tools for NOAA AFSC GAP.
 * 
 * @license BSD 3 Clause
 * @author Regents of University of California / The Eric and Wendy Schmidt
 *      Center for Data Science and the Environment at UC Berkeley.
 */


/**
 * Main presenter for the visualization.
 * 
 * Main presenter for the visualization which coordinates across sub-components
 * including the two displays.
 */
class VizPresenter {

    /**
     * Create a new presenter in global space.
     * 
     * Create a new presenter in global space where document wide coverage is
     * required due to certain event handlers. Note that this will build the
     * children presenters as appropriate.
     */
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

    /**
     * Determine if "dynamic scaling" is enabled.
     * 
     * @return {boolean} True if the scales should change between dataset
     *      subsets and false if a set of global static scales should be used
     *      instead.
     */
    _getDynamicScaling() {
        const self = this;

        const checkbox = document.getElementById("dynamic-scales-check");
        return checkbox.checked;
    }

    /**
     * Switch visualization to a new dataset.
     * 
     * Update all datasets / surveys in the visualization using current filter
     * configurations. This should be used when an entirelly new dataset is
     * under consideration and the availability of data for the frame currently
     * being considered needs to be recalculated. This happens, for example,
     * when changing area / region.
     */
    _refreshAllDatasets() {
        const self = this;

        self._display1.refreshDataset();
        self._display2.refreshDataset();
        self._updateDeeplink();
    }

    /**
     * Update a selection within an existing dataset subset.
     * 
     * Update the visualization to show a different subset of data within the
     * selected dataset. This is used, for example, when the survey remains the
     * same but the species or year has changed.
     */
    _refreshAllSelections() {
        const self = this;

        self._display1.refreshSelection();
        self._display2.refreshSelection();
        self._updateDeeplink();
    }

    /**
     * Update the URL status to reflect new user filter configurations.
     * 
     * Add a JSON string to the URL describing the user's current selection of
     * filters like selected area, species, and year. This is persisted as a
     * new state on the browser history.
     */
    _updateDeeplink() {
        const self = this;

        if (disableDeepLink) {
            return;
        }

        /**
         * Build a state sub-object for a species selection.
         * 
         * Build the subset of the state object describing a single species
         * selection including scientific name, common name, and year.
         * 
         * @param {SpeciesSelection} selection The selection to be converted to
         *      a state object.
         * @return {Object} Newly built state sub-object.
         */
        const buildSpeciesPayload = (selection) => {
            const isSciName = selection.getIsSciName();
            return {
                "scientificName": selection.getName(),
                "commonName": selection.getName(),
                "year": selection.getYear()
            };
        };

        /**
         * Build a state sub-object for a display selection.
         * 
         * Build the subset of the state object describing the selections for
         * a display including, for example, the species and the temperature
         * mode.
         * 
         * @param {DisplaySelection} selection The display-wide selections to
         *      be converted to a state sub-object.
         * @return {Object} Newly built state sub-object.
         */
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

    /**
     * Initialize or skip the intro presenter.
     * 
     * Determine if the intro should run based on deep link status and, if it,
     * should run, start an Intro presenter.
     */
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

    /**
     * Determine if the intro should be skipped or initalized.
     * 
     * Depending on the data loading status for the page, determine if the
     * intro should be initialized or skipped. Alternatively, determine if
     * no action on the intro should be taken yet.
     */
    _checkToStartIntro() {
        const self = this;

        // Wait to initalize or skip the intro after both displays are loaded
        // but only do it on the first load.
        self._displaysLoaded++;
        const shouldInitIntro = self._displaysLoaded == 2;
        if (shouldInitIntro) {
            self._startIntro();
            return;
        }

        // Force the introduction to re-sync control of visualization elements
        // if there is a resize during the intro sequence.
        const bothLoaded = self._displaysLoaded % 2 == 0;
        const introDone = self._intro === null || self._intro.isDone();
        if (self._resized && bothLoaded && !introDone) {
            self._intro.forceSync();
            self._resized = false;
        }
    }

    /**
     * Callback for when the user has selected a geohash.
     * 
     * @param {string} geohash The geohash selected by the user.
     */
    _onGeohashEnter(geohash) {
        const self = this;
        self._selectGeohash(geohash);
    }

    /**
     * Callback for when the user has unselected a geohash.
     * 
     * @param {string} geohash The geohash unselected by the user.
     */
    _onGeohashLeave(geohash) {
        const self = this;
        if (geohash === self._selectedGeohash) {
            self._selectGeohash(null);
        }
    }

    /**
     * Indicate that the user has selected a geohash.
     * 
     * @param {?string} geohash The geohash selected by the user or null if the
     *      user has indicated that no geohash should be selected.
     */
    _selectGeohash(geohash) {
        const self = this;
        self._selectedGeohash = geohash;
        self._display1.selectGeohash(geohash);
        self._display2.selectGeohash(geohash);
    }

}
