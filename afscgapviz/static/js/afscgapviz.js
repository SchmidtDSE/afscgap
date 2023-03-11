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
    }

    _refreshAllSelections() {
        const self = this;

        self._display1.refreshSelection();
        self._display2.refreshSelection();
    }

}
