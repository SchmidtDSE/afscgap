class SpeciesSelection {

    constructor(name, isSciName, year) {
        const self = this;
        self._name = name;
        self._isSciName = isSciName;
        self._year = year;
    }
    
    getName() {
        const self = this;
        return self._name;
    }
    
    getIsSciName() {
        const self = this;
        return self._isSciName;
    }
    
    getYear() {
        const self = this;
        return self._year;
    }

}


class SpeciesSelector {

    constructor(element, useSciName) {
        const self = this;

        self._element = element;
        self._useSciName = useSciName;

        self._refreshVisibility();
        self._registerCallbacks();
    }

    getSelection() {
        const self = this;

        const selector = self._getNameSelector();
        const name = self._getName(selector);

        const year = parseInt(
            self._element.querySelector(".year-select").value
        );

        return new SpeciesSelection(
            name,
            self._useSciName,
            year
        );
    }

    _refreshVisibility() {
        const self = this;

        if (self._useSciName) {
            self._show(".scientific-name-select");
            self._hide(".common-name-select");
        } else {
            self._hide(".scientific-name-select");
            self._show(".common-name-select");
        }

        const selector = self._getNameSelector();
        const name = self._getName(selector);
        const nameSet = name !== "None";

        if (nameSet) {
            self._show(".year-select");
        } else {
            self._hide(".year-select");
        }
    }

    _registerCallbacks() {
        const self = this;

        const selector = self._getNameSelector();
        self._element.querySelector(selector).addEventListener("change", () => {
            self._refreshVisibility();
        });
    }

    _getName(selector) {
        const self = this;

        const element = self._element.querySelector(selector);
        return element.value;
    }

    _show(selector) {
        const self = this;
        self._element.querySelector(selector).style.display = "block";
    }

    _hide(selector) {
        const self = this;
        self._element.querySelector(selector).style.display = "none";
    }

    _getNameSelector() {
        const self = this;

        const selectorPiece = self._useSciName ? "scientific" : "common";
        const selector = "." + selectorPiece + "-name-select";
        
        return selector;
    }

}
