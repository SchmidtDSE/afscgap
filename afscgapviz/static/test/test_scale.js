QUnit.module("scale", function() {

    QUnit.test("combine", function(assert) {
        const map1 = new Map();
        map1.set("a", 1);
        const summary1 = new Summary(
            1,
            2,
            null,
            null,
            -3,
            4,
            map1
        );

        const map2 = new Map();
        map2.set("b", 2);
        const summary2 = new Summary(
            10,
            20,
            30,
            40,
            null,
            null,
            map2
        );

        const combined = summary1.combine(summary2);

        assert.ok(combined.getMinCpue() == 1);
        assert.ok(combined.getMaxCpue() == 20);
        assert.ok(combined.getMinTemperature() == 30);
        assert.ok(combined.getMaxTemperature() == 40);
        assert.ok(combined.getMinTemperatureDelta() == -3);
        assert.ok(combined.getMaxTemperatureDelta() == 4);
        assert.ok(combined.getCpues().get("a") == 1);
        assert.ok(combined.getCpues().get("b") == 2);
    });

});