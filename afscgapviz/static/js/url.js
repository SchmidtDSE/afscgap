const GEOHASHES_ENDPOINT = "/geohashes.csv";
const PYTHON_ENDPOINT = "/example.py"


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

    if (secondSelection !== undefined && secondSelection.getName() !== "None") {
        params.push("comparison=y");
        params.push("otherYear=" + secondSelection.getYear());

        const secondName = secondSelection.getName();
        if (secondSelection.getIsSciName()) {
            params.push("otherSpecies=" + secondName);
        } else {
            params.push("otherCommonName=" + secondName);
        }
    }

    const queryString = params.join("&");
    const url = GEOHASHES_ENDPOINT + "?" + queryString;

    return url;
}


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

    if (secondSelection !== undefined && secondSelection.getName() !== "None") {
        params.push("comparison=y");
        params.push("otherYear=" + secondSelection.getYear());

        const secondName = secondSelection.getName();
        if (secondSelection.getIsSciName()) {
            params.push("otherSpecies=" + secondName);
        } else {
            params.push("otherCommonName=" + secondName);
        }
    }

    const queryString = params.join("&");
    const url = PYTHON_ENDPOINT + "?" + queryString;

    return url;
}
