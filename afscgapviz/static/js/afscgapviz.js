class VizPresenter {

    constructor() {
        const self = this;

        self._commonScale = new CommonScale(() => {
            return [
                () => self._display1.getSelection(),
                () => self._display2.getSelection()
            ];
        });

        self._display1 = new Display(
            document.getElementById("display-1"),
            self._commonScale,
            () => self._refreshAllDatasets(),
            () => self._refreshAllSelections()
        );
        self._display2 = new Display(
            document.getElementById("display-2"),
            self._commonScale,
            () => self._refreshAllDatasets(),
            () => self._refreshAllSelections()
        );
    }

    _refreshAllDatasets() {
        const self = this;

        self._display1.refreshDataset();
        self._display2.refreshDataset();
        self._updateDeeplink()
    }

    _refreshAllSelections() {
        const self = this;

        self._display1.refreshSelection();
        self._display2.refreshSelection();
        self._updateDeeplink()
    }

    _updateDeeplink() {
        const self = this;

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

}
