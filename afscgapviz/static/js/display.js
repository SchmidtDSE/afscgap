class Display {

    constructor(element) {
        const self = this;

        self._element = element;

        self._buildSpeciesDisplays();
        self._registerCallbacks();
    }

    _buildSpeciesDisplays() {
        const self = this;

        const nameType = self._element.querySelector(
            ".species-type-select"
        ).value;
        const useSciName = nameType === "scientific";

        self._speciesDisplayFirst = new SpeciesSelector(
            self._element.querySelector(".species-1"),
            useSciName
        );
        self._speciesDisplaySecond = new SpeciesSelector(
            self._element.querySelector(".species-2"),
            useSciName
        );
    }

    _registerCallbacks() {
        const self = this;

        const callback = () => self._onChange();

        self._element.querySelector(".species-type-select").addEventListener(
            "change",
            callback
        );
        self._element.querySelector(".area-select").addEventListener(
            "change",
            callback
        );
    }

    _onChange() {
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
            });
        };

        setTimeout(makeRequest, 500);
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
