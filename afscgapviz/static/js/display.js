/**
 * Logic for running a "display" which is a visualization and its controls.
 * 
 * Logic for running a "display" which is a visualization and its controls where
 * there are two displays on the page by default.
 * 
 * @license BSD 3 Clause
 * @author Regents of University of California / The Eric and Wendy Schmidt
 *      Center for Data Science and the Environment at UC Berkeley.
 */

/**
 * Object summarizing a user's configuration for a display.
 */
class DisplaySelection {

    /**
     * Create a new summary of a user's display configuration.
     * 
     * @param {string} survey The name of the survey selected by the user like
     *      "GOA" for Gulf of Alaska.
     * @param {string} temperatureMode The type of tepmerature the user wants
     *      displayed on the page or "disabled" if no temperature should be
     *      shown.
     * @param {SpeciesSelection} speciesSelection1 The first species selected
     *      by the user to be shown. This is expected to have getIsActive() is
     *      true.
     * @param {SpeciesSelection} speciesSelection2 The second species selected
     *      by the user to be shown which may not be active.
     */
    constructor(survey, temperatureMode, speciesSelection1, speciesSelection2) {
        const self = this;
        self._survey = survey;
        self._temperatureMode = temperatureMode;
        self._speciesSelection1 = speciesSelection1;
        self._speciesSelection2 = speciesSelection2;
    }
    
    /**
     * Get the name of the survey requested.
     * 
     * @return {string} The name of the survey selected by the user like "GOA"
     *      for Gulf of Alaska.
     */
    getSurvey() {
        const self = this;
        return self._survey;
    }
    
    /**
     * Get the type of temperature to display if any.
     * 
     * @return The type of temperature to display like "surface" or "bottom" or
     *      "disabled" if no temperature should be displayed.
     */
    getTemperatureMode() {
        const self = this;
        return self._temperatureMode;
    }
    
    /**
     * Get the first species / year to display within the display.
     * 
     * @return {SpeciesSelection} The first species selected by the user to be
     *      shown. This is expected to have getIsActive() is true.
     */
    getSpeciesSelection1() {
        const self = this;
        return self._speciesSelection1;
    }
    
    /**
     * Get the second species / year to display within the display.
     * 
     * @return {SpeciesSelection} The second species selected by the user to be
     *      shown which may not be active.
     */
    getSpeciesSelection2() {
        const self = this;
        return self._speciesSelection2;
    }

    /**
     * Determine if temperature data should be displayed.
     * 
     * @return {boolean} True if temperature data should be visualized and false
     *      otherwise.
     */
    getTemperatureEnabled() {
        const self = this;
        return self._temperatureMode !== "disabled";
    }

    /**
     * Get a key uniquely identifying this selection.
     * 
     * @return {string} Key uniquely identifying this selection such that two
     *      DisplaySelections with the same key have the same values.
     */
    getKey() {
        const self = this;
        return [
            self._survey,
            self._temperatureMode,
            self._speciesSelection1.getKey(),
            self._speciesSelection2.getKey()
        ].join("/");
    }

}


/**
 * Presenter for a display which manages a visualization and its controls.
 * 
 * Presenter for a display which manages a visualization and its controls but
 * delegates actual rendering and SVG management to a MapViz.
 */
class Display {

    /**
     * Create a new presenter for a display.
     * 
     * @param {number} number The 1-indexed ID of this display which may be
     *      required for certain event management, allowing this presenter to
     *      uniquely identify which display it is controlling.
     * @param {HTMLElement} element The root element of the display that this
     *      presenter is managing.
     * @param {CommonScale} commonScale A scale generator which coordinates
     *      across visualization elements to ensure consistent presentation.
     * @param {function} onDatasetChange Callback to invoke when the user
     *      changes the dataset (such as survey) of interest, requiring the
     *      evaluation of an entirelly new dataset.
     * @param {function} onSelectionChange Callback to invoke when the user
     *      changes the subset of the current dataset (such as species or year)
     *      which is of interest.
     * @param {function} onRender Callback for when this display finishes
     *      refreshing its display.
     * @param {function} onGeohashEnter Callback for when a user selects a
     *      geohash.
     * @param {function} onGeohashLeave Callback for when a user unselects a
     *      geohash.
     */
    constructor(number, element, commonScale, onDatasetChange,
        onSelectionChange, onRender, onGeohashEnter, onGeohashLeave) {
        const self = this;

        self._number = number;
        self._element = element;
        self._commonScale = commonScale;
        self._onDatasetChange = onDatasetChange;
        self._onSelectionChange = onSelectionChange;
        self._onRender = onRender;
        self._onGeohashEnter = onGeohashEnter;
        self._onGeohashLeave = onGeohashLeave;
        self._mapViz = null;
        self._previousWidth = self._getMapWidth();

        self._buildSpeciesDisplays();
        self._rebuildMap();
        self._registerCallbacks();
        self._updateDownloadLinks();
    }

    /**
     * Get the user's current selection of filters.
     * 
     * @return {DisplaySelection} Information about the dataset and subset
     *      requested by the user as configured by the HTML elements on the
     *      page.
     */
    getSelection() {
        const self = this;
        
        const survey = self._element.querySelector(".area-select").value;
        const temperatureMode = self._element.querySelector(
            ".temperature-select"
        ).value;
        const speciesSelection1 = self._speciesDisplayFirst.getSelection();
        const speciesSelection2 = self._speciesDisplaySecond.getSelection();

        return new DisplaySelection(
            survey,
            temperatureMode,
            speciesSelection1,
            speciesSelection2
        );
    }

    /**
     * Highlight and show information about a geohash within this visualization.
     * 
     * @param {?string} geohash The geohash to highlight in the map and for
     *      which data should be shown in the title or null if no geohash
     *      should be highlighted / shown.
     */
    selectGeohash(geohash) {
        const self = this;
        
        if (self._mapViz === null) {
            return;
        }

        self._mapViz.selectGeohash(geohash);
    }

    /**
     * Instruct this display to update its dataset.
     * 
     * Instruct this display to update its dataset using its current selection,
     * requesting new data from the server in the process.
     */
    refreshDataset() {
        const self = this;

        self._changeSurveyLoading(true);

        /**
         * Actually execute the request.
         */
        const makeRequest = () => {
            fetch(self._generateSurveyPanelUrl()).then((response) => {
                return response.text();
            }).then((text) => {
                const speciesSelects = self._element.querySelector(
                    ".species-selects"
                );
                speciesSelects.innerHTML = text;

                if (!allowSpecies2) {
                    const species2 = self._element.querySelector(".species-2");
                    species2.style.display = "none";
                    species2.style.opacity = 0;
                }

                self._buildSpeciesDisplays();
                self._changeSurveyLoading(false);
                self._onSelectionChange();
            });
        };

        setTimeout(makeRequest, 500);
    }

    /**
     * Instruct this display to refresh its current dataset subset.
     * 
     * Instruct this display to change or refresh which subset of the current
     * dataset is shown. This will cause detailed data on the map to be re-
     * requested but dataset availability metadata will remain the same.
     */
    refreshSelection() {
        const self = this;

        self._mapViz.updateSelection(self.getSelection());
    }

    _getMapWidth() {
        const self = this;
        const vizElement = self._element.querySelector(".viz");
        return vizElement.getBoundingClientRect().width;
    }

    /**
     * Build the selection interface for the two species / scatters.
     */
    _buildSpeciesDisplays() {
        const self = this;

        const nameType = self._element.querySelector(
            ".species-type-select"
        ).value;
        const useSciName = nameType === "scientific";

        self._speciesDisplayFirst = new SpeciesSelector(
            self._element.querySelector(".species-1"),
            useSciName,
            () => {
                self._updateDownloadLinks();
                self._onSelectionChange();
            }
        );
        self._speciesDisplaySecond = new SpeciesSelector(
            self._element.querySelector(".species-2"),
            useSciName,
            () => {
                self._updateDownloadLinks();
                self._onSelectionChange();
            }
        );
    }

    /**
     * Attach internal callbacks for this presenter.
     */
    _registerCallbacks() {
        const self = this;

        self._element.querySelector(".species-type-select").addEventListener(
            "change",
            () => {
                self._updateDownloadLinks();
                self._onDatasetChange();
            }
        );
        self._element.querySelector(".area-select").addEventListener(
            "change",
            () => {
                self._updateDownloadLinks();
                self._onDatasetChange();
            }
        );
        self._element.querySelector(".temperature-select").addEventListener(
            "change",
            () => {
                self._updateDownloadLinks();
                self._onDatasetChange();
            }
        );

        let timeout; 
        addEventListener("resize", () => {
            if (disableResizeRefresh) {
                return;
            }

            clearTimeout(timeout);
            timeout = setTimeout(() => {
                const newWidth = self._getMapWidth();
                if (Math.abs(newWidth - self._previousWidth) > 20) {
                    self._rebuildMap();
                    self._previousWidth = newWidth;
                }
            }, 1000);
        });
    }

    /**
     * Update the hrefs for the links which allow the user to download data or
     * example scripts.
     */
    _updateDownloadLinks() {
        const self = this;

        const selection = self.getSelection();

        /**
         * Update the link on the download data button.
         * 
         * @param {DisplaySelection} selection The current selection chosen by
         *      the user.
         */
        const updateDownloadDataButton = (selection) => {
            const newUrl = generateDownloadDataUrl(
                selection.getSurvey(),
                selection.getSpeciesSelection1(),
                selection.getSpeciesSelection2(),
                5
            );

            const downloadUrl = self._element.querySelector('.download-link');
            downloadUrl.href = newUrl;

            if (selection.getSpeciesSelection2().getIsActive()) {
                downloadUrl.innerHTML = "Download Comparison";
            } else {
                downloadUrl.innerHTML = "Download Data";
            }
        };

        /**
         * Update the link on the download Python example button.
         * 
         * @param {DisplaySelection} selection The current selection chosen by
         *      the user.
         */
        const updatePythonButton = (selection) => {
            const newUrl = generatePythonUrl(
                selection.getSurvey(),
                selection.getSpeciesSelection1(),
                selection.getSpeciesSelection2()
            );

            const downloadUrl = self._element.querySelector('.python-link');
            downloadUrl.href = newUrl;
        }

        updateDownloadDataButton(selection);
        updatePythonButton(selection);
    }

    /**
     * Create a new map visualization presenter after resizing the viz SVG.
     */
    _rebuildMap() {
        const self = this;

        const vizElement = self._element.querySelector(".viz");

        const expectedHeight = Math.round(
            self._getMapWidth() * 0.55
        );
        vizElement.style.height = expectedHeight + "px";

        self._mapViz = new MapViz(
            self._element.querySelector(".viz-panel"),
            self.getSelection(),
            self._commonScale,
            self._onRender,
            self._onGeohashEnter,
            self._onGeohashLeave
        );
    }

    /**
     * Generate a URL where server side rendering of a species selection UI
     * can be requested. Note that server side rendering is desireable in this
     * case due to a number of database interactions required.
     */
    _generateSurveyPanelUrl() {
        const area = self._element.querySelector(".area-select").value;
        const speciesSelection1 = self._speciesDisplayFirst.getSelection();
        const speciesSelection2 = self._speciesDisplaySecond.getSelection();

        return generateSurveyPanelUrl(
            area,
            self._number,
            speciesSelection1,
            speciesSelection2
        );
    }

    /**
     * Update the loading spinner for the survey selection UI.
     * 
     * @param {boolean} stillLoading True if the loading spinner should be shown
     *      and false otherwise.
     */
    _changeSurveyLoading(stillLoading) {
        const self = this;

        const loadingIndicator = self._element.querySelector(".survey-loading");
        loadingIndicator.style.display = stillLoading ? "block" : "none";

        const surveyFields = self._element.querySelector(
            ".survey-specific-fields"
        );
        surveyFields.style.display = stillLoading ? "none": "block";
    }

}
