QUnit.module("mapviz", function() {

    const testDatum = new MapDatum(
        "abcd",
        10,
        20,
        30,
        40,
        5,
        67
    );

    QUnit.test("getCenterX", function(assert) {
        assert.ok(Math.abs(testDatum.getCenterX() - 25) < 0.0001);
    });

    QUnit.test("getCenterY", function(assert) {
        assert.ok(Math.abs(testDatum.getCenterY() - 40) < 0.0001);
    });

});