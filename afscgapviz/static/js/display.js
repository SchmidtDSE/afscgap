class DisplaySelection {

    constructor(survey, temperatureMode, speciesSelection1, speciesSelection2) {
        const self = this;
        self._survey = survey;
        self._temperatureMode = temperatureMode;
        self._speciesSelection1 = speciesSelection1;
        self._speciesSelection2 = speciesSelection2;
    }
    
    
    getSurvey() {
        const self = this;
        return self._survey;
    }
    
    getTemperatureMode() {
        const self = this;
        return self._temperatureMode;
    }
    
    getSpeciesSelection1() {
        const self = this;
        return self._speciesSelection1;
    }
    
    getSpeciesSelection2() {
        const self = this;
        return self._speciesSelection2;
    }

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


class Display {

    constructor(element, commonScale, onDatasetChange, onSelectionChange) {
        const self = this;

        self._element = element;
        self._commonScale = commonScale;
        self._onDatasetChange = onDatasetChange;
        self._onSelectionChange = onSelectionChange;

        self._buildSpeciesDisplays();
        self._rebuildMap();
        self._registerCallbacks();
    }

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

    _buildSpeciesDisplays() {
        const self = this;

        const nameType = self._element.querySelector(
            ".species-type-select"
        ).value;
        const useSciName = nameType === "scientific";

        self._speciesDisplayFirst = new SpeciesSelector(
            self._element.querySelector(".species-1"),
            useSciName,
            () => self._onSelectionChange()
        );
        self._speciesDisplaySecond = new SpeciesSelector(
            self._element.querySelector(".species-2"),
            useSciName,
            () => self._onSelectionChange()
        );
    }

    _registerCallbacks() {
        const self = this;

        self._element.querySelector(".species-type-select").addEventListener(
            "change",
            () => self._onDatasetChange()
        );
        self._element.querySelector(".area-select").addEventListener(
            "change",
            () => self._onDatasetChange()
        );
        self._element.querySelector(".temperature-select").addEventListener(
            "change",
            () => self._onDatasetChange()
        );

        let timeout; 
        addEventListener("resize", () => {
            clearTimeout(timeout);
            timeout = setTimeout(() => self._rebuildMap(), 500);
        });
    }

    refreshDataset() {
        const self = this;

        self._changeSurveyLoading(true);

        const makeRequest = () => {
                fetch(self._generateSurveyPanelUrl()).then((response) => {
                return response.text();
            }).then((text) => {
                const speciesSelects = self._element.querySelector(
                    ".species-selects"
                );
                speciesSelects.innerHTML = text;

                self._buildSpeciesDisplays();
                self._changeSurveyLoading(false);
                self._onSelectionChange();
            });
        };

        setTimeout(makeRequest, 500);
    }

    refreshSelection() {
        const self = this;

        self._mapViz.updateSelection(self.getSelection());
    }

    _rebuildMap() {
        const self = this;

        const vizElement = self._element.querySelector(".viz");
        const expectedHeight = Math.round(
            vizElement.getBoundingClientRect().width * 0.4
        );
        
        vizElement.style.height = expectedHeight + "px";

        self._mapViz = new MapViz(
            self._element.querySelector(".viz-panel"),
            self.getSelection(),
            self._commonScale
        );
    }

    _generateSurveyPanelUrl() {
        const self = this;

        const area = self._element.querySelector(".area-select").value;
        const url = '/speciesSelector/' + area + '.html';

        const speciesSelection1 = self._speciesDisplayFirst.getSelection();
        const species1Query = [
            "name1=" + speciesSelection1.getName(),
            "year1=" + speciesSelection1.getYear()
        ].join("&");

        const speciesSelection2 = self._speciesDisplaySecond.getSelection();
        const species2Query = [
            "name2=" + speciesSelection2.getName(),
            "year2=" + speciesSelection2.getYear()
        ].join("&");

        return url + "?" + species1Query + "&" + species2Query;
    }

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
