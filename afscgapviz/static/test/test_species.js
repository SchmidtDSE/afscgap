QUnit.module("species", function() {

    QUnit.test("getIsActive true", function(assert) {
        const selection = new SpeciesSelection(
            "Pacific cod",
            false,
            2021
        );

        assert.ok(selection.getIsActive() == true);
    });

    QUnit.test("getIsActive false", function(assert) {
        const selection = new SpeciesSelection(
            "None",
            false,
            2021
        );

        assert.ok(selection.getIsActive() == false); 
    });

    QUnit.test("getKey equal", function(assert) {
        const selection1 = new SpeciesSelection(
            "Pacific cod",
            false,
            2021
        );

        const selection2 = new SpeciesSelection(
            "Pacific cod",
            false,
            2021
        );

        assert.ok(selection1.getKey() === selection2.getKey());
    });

    QUnit.test("getKey not equal", function(assert) {
        const selection1 = new SpeciesSelection(
            "Pacific cod",
            false,
            2021
        );

        const selection2 = new SpeciesSelection(
            "None",
            false,
            2021
        );

        assert.ok(selection1.getKey() !== selection2.getKey());
    });

});
