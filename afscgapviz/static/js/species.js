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

    getKey() {
        const self = this;
        return [
            self._name,
            self._isSciName ? "y" : "n",
            self._year + ""
        ].join("/");
    }

    getIsActive() {
        const self = this;
        return self._name !== "None";
    }

}


class SpeciesSelector {

    constructor(element, useSciName, onChange) {
        const self = this;

        self._element = element;
        self._useSciName = useSciName;

        self._refreshVisibility();
        self._registerCallbacks();
        self._onChange = onChange;
    }

    getSelection() {
        const self = this;

        const query = self._getNameQuery();
        const name = self._getName(query);

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

        const query = self._getNameQuery();
        const name = self._getName(query);
        const nameSet = name !== "None";

        if (nameSet) {
            self._show(".year-select");
        } else {
            self._hide(".year-select");
        }
    }

    _registerCallbacks() {
        const self = this;

        const query = self._getNameQuery();
        self._element.querySelector(query).addEventListener("change", () => {
            self._refreshVisibility();
            self._onChange();
        });

        const yearDropdown = self._element.querySelector(".year-select");
        yearDropdown.addEventListener("change", () => {
            self._onChange();
        });
    }

    _getName(query) {
        const self = this;

        const element = self._element.querySelector(query);
        return element.value;
    }

    _show(query) {
        const self = this;
        self._element.querySelector(query).style.display = "block";
    }

    _hide(query) {
        const self = this;
        self._element.querySelector(query).style.display = "none";
    }

    _getNameQuery() {
        const self = this;

        const selectorPiece = self._useSciName ? "scientific" : "common";
        const selector = "." + selectorPiece + "-name-select";
        
        return selector;
    }

}
