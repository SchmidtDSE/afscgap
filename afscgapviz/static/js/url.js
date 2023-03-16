/**
 * Utilities for generating URLs for interacting with the server.
 * 
 * @license BSD 3 Clause
 * @author Regents of University of California / The Eric and Wendy Schmidt
 *      Center for Data Science and the Environment at UC Berkeley.
 */

const GEOHASHES_ENDPOINT = "/geohashes.csv";
const PYTHON_ENDPOINT = "/example.py"


/**
 * Determine where the geohash level data can be requested.
 * 
 * @param {string} survey The name of the survey for which data are requested
 *      like GOA.
 * @param {SpeciesSelection} speciesSelection The species and year requested.
 * @param {?SpeciesSelection} secondSelection The second "overlay" species and
 *      year requested if there are two species displayed. Pass undefined if
 *      no second species selection data available.
 * @param {number} geohashSize The number of characters requested in the geohash
 *      like 4 or 5 characters.
 */
function generateDownloadDataUrl(survey, speciesSelection, secondSelection,
    geohashSize) {

    const params = [
        "survey=" + survey,
        "year=" + speciesSelection.getYear(),
        "geohashSize=" + geohashSize
    ];

    if (speciesSelection.getIsSciName()) {
        params.push("species=" + speciesSelection.getName());
    } else {
        params.push("commonName=" + speciesSelection.getName());
    }

    if (secondSelection !== undefined && secondSelection.getIsActive()) {
        params.push("comparison=y");
        params.push("otherYear=" + secondSelection.getYear());

        const secondName = secondSelection.getName();
        if (secondSelection.getIsSciName()) {
            params.push("otherSpecies=" + secondName);
        } else {
            params.push("otherCommonName=" + secondName);
        }
    } else {
        params.push("comparison=n");
    }

    const queryString = params.join("&");
    const url = GEOHASHES_ENDPOINT + "?" + queryString;

    return url;
}


/**
 * Generate a URL where Python example code can be requested.
 * 
 * @param {string} survey The survey desired like GOA.
 * @param {SpeciesSelection} speciesSelection The first species requested for
 *      the display.
 * @param {?SpeciesSelection} secondSelection The second species requested for
 *      the display or undefined if only one species selection available.
 */
function generatePythonUrl(survey, speciesSelection, secondSelection) {
    const params = [
        "survey=" + survey,
        "year=" + speciesSelection.getYear()
    ];

    if (speciesSelection.getIsSciName()) {
        params.push("species=" + speciesSelection.getName());
    } else {
        params.push("commonName=" + speciesSelection.getName());
    }

    if (secondSelection !== undefined && secondSelection.getIsActive()) {
        params.push("comparison=y");
        params.push("otherYear=" + secondSelection.getYear());

        const secondName = secondSelection.getName();
        if (secondSelection.getIsSciName()) {
            params.push("otherSpecies=" + secondName);
        } else {
            params.push("otherCommonName=" + secondName);
        }
    } else {
        params.push("comparison=n");
    }

    const queryString = params.join("&");
    const url = PYTHON_ENDPOINT + "?" + queryString;

    return url;
}


/**
 * Generate a URL for survey side speices selection rendering.
 * 
 * Generate a URL where server side rendering of a species selection UI
 * can be requested. Note that server side rendering is desireable in this
 * case due to a number of database interactions required.
 * 
 * @param {string} area The name of the area requested like GOA.
 * @param {number} number The index of the display like 1 or 2.
 * @param {SpeciesSelection} speciesSelection1 The first species currently
 *      selected or the first default species if no selection has been made.
 * @param {SpeciesSelection} speciesSelection1 The second species currently
 *      selected or the second default species if no selection has been made.
 */
function generateSurveyPanelUrl(area, number, speciesSelection1,
    speciesSelection2) {
    const url = '/speciesSelector/' + area + '.html?index=' + number;

    const species1Query = [
        "name1=" + speciesSelection1.getName(),
        "year1=" + speciesSelection1.getYear()
    ].join("&");

    const species2Query = [
        "name2=" + speciesSelection2.getName(),
        "year2=" + speciesSelection2.getYear()
    ].join("&");

    return url + "&" + species1Query + "&" + species2Query;
}


/**
 * Generate a URL for getting dataset summary statistics.
 * 
 * @param {DisplaySelection} displaySelection The display-level selections with
 *      dataset definition like region.
 * @param {SpeciesSelection} speciesSelection The first species selected for the
 *      display.
 * @param {number} geohashSize The size (like 4 or 5) of the geohash desired in
 *      terms of numbers of characters.
 * @param {?SpeciesSelection} otherSpeciesSelection The second species selected
 *      for the display or undefined if no second species.
 * @return {string} URL at which the summary statistics report can be found.
 */
function generateSummarizeUrl(displaySelection, speciesSelection, geohashSize,
    otherSpeciesSelection) {
    let isComparison = true;
    if (otherSpeciesSelection === undefined) {
        isComparison = false;
    } else if (!otherSpeciesSelection.getIsActive()) {
        isComparison = false;
    }

    const params = [
        "survey=" + displaySelection.getSurvey(),
        "year=" + speciesSelection.getYear(),
        "temperature=" + displaySelection.getTemperatureMode(),
        "geohashSize=" + geohashSize,
        "comparison=" + (isComparison ? "y" : "n")
    ];

    if (speciesSelection.getIsSciName()) {
        params.push("species=" + speciesSelection.getName());
    } else {
        params.push("commonName=" + speciesSelection.getName());
    }

    if (isComparison) {
        params.push("otherYear=" + otherSpeciesSelection.getYear());
        if (otherSpeciesSelection.getIsSciName()) {
            params.push("otherSpecies=" + otherSpeciesSelection.getName());
        } else {
            params.push("otherCommonName=" + otherSpeciesSelection.getName());
        }
    }

    const queryString = params.join("&");
    const url = "/summarize.json?" + queryString;

    return url;
}

