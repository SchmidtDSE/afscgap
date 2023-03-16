QUnit.module("species", function() {

    const speciesSelection = new SpeciesSelection(
        "Pacific cod",
        false,
        2021
    );

    const speciesSelectionOther = new SpeciesSelection(
        "Other",
        true,
        2022
    );

    const speciesSelectionDisabled = new SpeciesSelection(
        "None",
        false,
        2021
    );

    const displaySelection = new DisplaySelection(
        "GOA",
        "disabled",
        speciesSelection,
        speciesSelection
    );

    QUnit.test("generateDownloadDataUrl no comparison", function(assert) {
        const url = generateDownloadDataUrl(
            "GOA",
            speciesSelection,
            speciesSelectionDisabled,
            4
        );

        const assertFound = (substring) => {
            assert.ok(url.indexOf(substring) != -1);
        };

        assertFound("survey=GOA");
        assertFound("year=2021");
        assertFound("geohashSize=4");
        assertFound("commonName=Pacific cod");
        assertFound("comparison=n");
    });

    QUnit.test("generateDownloadDataUrl comparison", function(assert) {
        const url = generateDownloadDataUrl(
            "GOA",
            speciesSelection,
            speciesSelectionOther,
            4
        );

        const assertFound = (substring) => {
            assert.ok(url.indexOf(substring) != -1);
        };

        assertFound("survey=GOA");
        assertFound("year=2021");
        assertFound("geohashSize=4");
        assertFound("commonName=Pacific cod");
        assertFound("comparison=y");
        assertFound("otherYear=2022");
        assertFound("otherSpecies=Other");
    });

    QUnit.test("generatePythonUrl no comparison", function(assert) {
        const url = generatePythonUrl(
            "GOA",
            speciesSelection,
            speciesSelectionDisabled
        );

        const assertFound = (substring) => {
            assert.ok(url.indexOf(substring) != -1);
        };

        assertFound("survey=GOA");
        assertFound("year=2021");
        assertFound("commonName=Pacific cod");
        assertFound("comparison=n");
    });

    QUnit.test("generatePythonUrl comparison", function(assert) {
        const url = generatePythonUrl(
            "GOA",
            speciesSelection,
            speciesSelectionOther
        );

        const assertFound = (substring) => {
            assert.ok(url.indexOf(substring) != -1);
        };

        assertFound("survey=GOA");
        assertFound("year=2021");
        assertFound("commonName=Pacific cod");
        assertFound("comparison=y");
        assertFound("otherYear=2022");
        assertFound("otherSpecies=Other");
    });

    QUnit.test("generateSurveyPanelUrl no comparison", function(assert) {
        const url = generateSurveyPanelUrl(
            "GOA",
            1,
            speciesSelection,
            speciesSelectionDisabled
        );

        const assertFound = (substring) => {
            assert.ok(url.indexOf(substring) != -1);
        };

        assertFound("/speciesSelector/GOA.html");
        assertFound("index=1");
        assertFound("name1=Pacific cod");
        assertFound("year1=2021");
        assertFound("name2=None");
    });

    QUnit.test("generateSurveyPanelUrl comparison", function(assert) {
        const url = generateSurveyPanelUrl(
            "GOA",
            1,
            speciesSelection,
            speciesSelectionOther
        );

        const assertFound = (substring) => {
            assert.ok(url.indexOf(substring) != -1);
        };

        assertFound("/speciesSelector/GOA.html");
        assertFound("index=1");
        assertFound("name1=Pacific cod");
        assertFound("year1=2021");
        assertFound("name2=Other");
        assertFound("year2=2022");
    });

    QUnit.test("generateSummarizeUrl no comparison", function(assert) {
        const url = generateSummarizeUrl(
            displaySelection,
            speciesSelection,
            4,
            speciesSelectionDisabled
        );

        const assertFound = (substring) => {
            assert.ok(url.indexOf(substring) != -1);
        };

        assertFound("survey=GOA");
        assertFound("year=2021");
        assertFound("temperature=disabled");
        assertFound("geohashSize=4");
        assertFound("commonName=Pacific cod");
        assertFound("comparison=n");
    });

    QUnit.test("generateSummarizeUrl comparison", function(assert) {
        const url = generateSummarizeUrl(
            displaySelection,
            speciesSelection,
            4,
            speciesSelectionOther
        );

        const assertFound = (substring) => {
            assert.ok(url.indexOf(substring) != -1);
        };

        assertFound("survey=GOA");
        assertFound("year=2021");
        assertFound("temperature=disabled");
        assertFound("geohashSize=4");
        assertFound("commonName=Pacific cod");
        assertFound("comparison=y");
        assertFound("otherYear=2022");
        assertFound("otherSpecies=Other");
    });

});