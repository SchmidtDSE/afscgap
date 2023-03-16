QUnit.module("display", function() {

    const speciesSelection = new SpeciesSelection(
        "Pacific cod",
        false,
        2021
    );

    QUnit.test("getTemperatureEnabled true", function(assert) {
        const selection = new DisplaySelection(
            "GOA",
            "surface",
            speciesSelection,
            speciesSelection
        );

        assert.ok(selection.getTemperatureEnabled() == true);
    });

    QUnit.test("getTemperatureEnabled false", function(assert) {
        const selection = new DisplaySelection(
            "GOA",
            "disabled",
            speciesSelection,
            speciesSelection
        );

        assert.ok(selection.getTemperatureEnabled() == false); 
    });

    QUnit.test("getKey equal", function(assert) {
        const selection1 = new DisplaySelection(
            "GOA",
            "surface",
            speciesSelection,
            speciesSelection
        );

        const selection2 = new DisplaySelection(
            "GOA",
            "surface",
            speciesSelection,
            speciesSelection
        );

        assert.ok(selection1.getKey() === selection2.getKey());
    });

    QUnit.test("getKey not equal", function(assert) {
        const selection1 = new DisplaySelection(
            "GOA",
            "surface",
            speciesSelection,
            speciesSelection
        );

        const selection2 = new DisplaySelection(
            "GOA",
            "disabled",
            speciesSelection,
            speciesSelection
        );

        assert.ok(selection1.getKey() !== selection2.getKey()); 
    });

});
