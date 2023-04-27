/**
 * Utilities and logic for running the species selection interface.
 * 
 * @license BSD 3 Clause
 * @author Regents of University of California / The Eric and Wendy Schmidt
 *      Center for Data Science and the Environment at UC Berkeley.
 */


/**
 * Record of a selection of a specific species within a year.
 */
class SpeciesSelection {

    /**
     * Create a new record of species selection within a year.
     * 
     * @param {string} name The name of the species.
     * @param {boolean} isSciName Flag indicating if the species name given is
     *      a scientific or common name. True if a scientific name and false
     *      otherwise.
     * @param {number} year The year of data selected.
     */
    constructor(name, isSciName, year) {
        const self = this;
        self._name = name;
        self._isSciName = isSciName;
        self._year = year;
    }
    
    /**
     * Get the name of the species selected.
     * 
     * @return {string} The name of the species.
     */
    getName() {
        const self = this;
        return self._name;
    }
    
    /**
     * Determine if the name selected is a scientific or common name.
     * 
     * @return {boolean} Flag indicating if the species name given is a
     *      scientific or common name. True if a scientific name and false
     *      otherwise.
     */
    getIsSciName() {
        const self = this;
        return self._isSciName;
    }
    
    /**
     * Get the year selected by the user.
     * 
     * @return {number} Year selected by the user.
     */
    getYear() {
        const self = this;
        return self._year;
    }

    /**
     * Get a string describing this selection.
     * 
     * @return {string} String which, if two SpeciesSelections have the same
     *      key, they have the same values.
     */
    getKey() {
        const self = this;
        return [
            self._name,
            self._isSciName ? "y" : "n",
            self._year + ""
        ].join("/");
    }

    /**
     * Determine if this selection is for no species.
     * 
     * @return {boolean} False if this selection is "disabled" or for no species
     *      to be selected. True otherwise.
     */
    getIsActive() {
        const self = this;
        return self._name !== "None";
    }

}


/**
 * Presenter for a species selector.
 */
class SpeciesSelector {

    /**
     * Create a new species selector presenter.
     * 
     * @param {HTMLElement} element The root element of the selector UI.
     * @param {boolean} useSciName Flag indicating if the user should be shown
     *      species with their scientific name or their common name. True if
     *      scientific name and false otherwise.
     * @param {function} onChange Function to call when the user changes their
     *      species selection.
     */
    constructor(element, useSciName, onChange) {
        const self = this;

        self._element = element;
        self._useSciName = useSciName;

        self._refreshVisibility();
        self._registerCallbacks();
        self._onChange = onChange;
    }

    /**
     * Get the currently selected species / year selection.
     * 
     * @return {SepeciesSelection} Record describing which speices the user has
     *      selected and in which year.
     */
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

    /**
     * Change which UI elements are shown to the user.
     * 
     * Change which UI elements are shown to the user based on what kind of name
     * the user is selecting (scientific v common) and if a speices has been
     * selected or if it is disabled / no species selected.
     */
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

    /**
     * Register internal event listeners.
     */
    _registerCallbacks() {
        const self = this;

        const query = self._getNameQuery();
        let callback = null;
        const speciesOptions = [];
        const speciesElement = self._element.querySelector(query);
        const speciesList = speciesElement.list;
        for (const child of speciesList.children) {
            speciesOptions.push(child.value.toLowerCase());
        }
        speciesElement.addEventListener("input", () => {
            clearTimeout(callback);
            callback = setTimeout(
                () => {
                    const lowerInputValue = speciesElement.value.toLowerCase();
                    if (speciesOptions.indexOf(lowerInputValue) != -1) {
                        self._refreshVisibility();
                        self._onChange();
                    }
                },
                500
            );
        });

        const yearDropdown = self._element.querySelector(".year-select");
        yearDropdown.addEventListener("change", () => {
            self._onChange();
        });
    }

    /**
     * Get the species name currently selected by the user.
     * 
     * @return {string} Currently selected species name.
     */
    _getName(query) {
        const self = this;

        const element = self._element.querySelector(query);
        return element.value;
    }

    /**
     * Show a sub element of this UI component.
     * 
     * @param {string} query The query selector to use (as a child of this UI's
     *      root element) to find the element to display.
     */
    _show(query) {
        const self = this;
        self._element.querySelector(query).style.display = "block";
    }

    /**
     * Hide a sub element of this UI component.
     * 
     * @param {string} query The query selector to use (as a child of this UI's
     *      root element) to find the element to hide.
     */
    _hide(query) {
        const self = this;
        self._element.querySelector(query).style.display = "none";
    }

    /**
     * Determine which select should be leveraged by the user in selecting a
     * species depending on if scientific or common names are enabled.
     */
    _getNameQuery() {
        const self = this;

        const selectorPiece = self._useSciName ? "scientific" : "common";
        const selector = "." + selectorPiece + "-name-select";
        
        return selector;
    }

}
