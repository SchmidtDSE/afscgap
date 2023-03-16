QUnit.module("scale", function() {

    QUnit.test("combine", function(assert) {
        const summary1 = new Summary(
            1,
            2,
            null,
            null,
            -3,
            4
        );

        const summary2 = new Summary(
            10,
            20,
            30,
            40,
            null,
            null
        );

        const combined = summary1.combine(summary2);

        assert.ok(combined.getMinCpue(), 1);
        assert.ok(combined.getMaxCpue(), 20);
        assert.ok(combined.getMinTemperature(), 30);
        assert.ok(combined.getMaxTemperature(), 40);
        assert.ok(combined.getMinTemperatureDelta(), -3);
        assert.ok(combined.getMaxTemperatureDelta(), 4);
    });

});