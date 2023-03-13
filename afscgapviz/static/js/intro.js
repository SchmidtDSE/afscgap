const STEP_TEXTS = [
    "Hello! This visualization explores data from NOAA (AFSC GAP) in and around Alaska.",
    "This is a map of the Gulf of Alaska and these squares show areas where a survey has been taken to determine which fish are present.",
    "For example, these are catch reports for the economically important Pacific cod species. This is in terms of density or, in other words, weight of cod caught during a survey relative to area surveyed.",
    "Contrast this with the cod numbers from 2021 and note that the catches have gotten smaller, espeically around Kodiak Island in the middle.",
    "What happened here? Well, consider The Blob warming event which took place in 2015. Try changing the date on the second display from 2021 to 2015.",
    "Even mid-event, signs of decreased catch starting to show up. Now, let's take a look at the warming. Select bottom temperatures in both displays. How did they change between years?",
    "It looksl ike there may have been some warming in the Gulf of Alaska what about the Aleutian Islands? Did the same temperatures appear there? Try putting 2015 Gulf of Alaska data in one display and 2015 Aleutian Islands data in the other.",
    "To better see this, let's overlay the data. On one display, let's put 2013 as Scatter 1 vs 2015 as Scatter 2 for Pacific cod in the Gulf of Alaksa.",
    "Then, let's do the same in the Aleutian Islands in the other dislpay. Make sure bottom temperature is displayed on both to see how temperatures changed in the region.",
    "With these temperature changes displayed, how did the catch change in areas of warming? Unfortunately, climate change may make this more common.",
    "This is a lot of info on Pacific cod. How about walleye pollock? Did that species see something similar happen? Go ahead and explore that species below.",
    "That's it for the intro! Want to learn more about this? See our <a target='_blank' href='https://mybinder.org/v2/gh/SchmidtDSE/afscgap/main?urlpath=/tree/index.ipynb'>example notebook</a>."
];


class Intro {

    constructor() {
        const self = this;
        self._step = 0;

        self._registerCallbacks();

        document.getElementById("intro-text").innerHTML = STEP_TEXTS[0];
        d3.select("#intro-links").transition().style("opacity", 1);

        self._stepActions = [
            [],
            ["#display-1", ".land", ".water"],
            [".fish", ".radius-legend-holder", ".graph-description"],
            ["#display-2"],
            [".species-1"],
            [".temperature-select"],
            [".area-select", ".species-type-select"],
            [".species-2"],
            [".download-panel"],
            [],
            []
        ];

        self._stepActions.forEach((actions) => {
            actions.forEach((action) => {
                d3.selectAll(action).attr("originalDisplay", function() {
                    return this.style.display;
                });
                d3.selectAll(action).style("display", "none");
                d3.selectAll(action).style("opacity", "0");
            });
        });

        self._updateLinkVisibility();
    }

    _registerCallbacks() {
        const self = this;
        document.getElementById("skip-intro-link").addEventListener(
            "click",
            () => self._skipIntro()
        );

        document.getElementById("back-link").addEventListener(
            "click",
            () => self._backStep()
        );

        document.getElementById("next-link").addEventListener(
            "click",
            () => self._nextStep()
        );
    }

    _skipIntro() {
        const self = this;

        self._stepActions.forEach((actions) => {
            actions.forEach((action) => {
                d3.selectAll(action).style("display", function() {
                    return this.getAttribute("originalDisplay");
                });
                d3.selectAll(action).transition().style("opacity", 1);
            });
        });

        document.getElementById("tutorial-panel").style.display = "none";
    }

    _backStep() {
        const self = this;
        self._step--;
        
        const newText = STEP_TEXTS[self._step];
        document.getElementById("intro-text").innerHTML = newText;
        
        self._updateLinkVisibility();
    }

    _nextStep() {
        const self = this;
        self._step++;
        
        self._stepActions[self._step].forEach((action, i) => {
            d3.selectAll(action).style("display", function() {
                return this.originalDisplay;
            });
            d3.selectAll(action).transition()
                .delay(i * 500 + 500)
                .style("opacity", 1);
        });
        const newText = STEP_TEXTS[self._step];
        document.getElementById("intro-text").innerHTML = newText;

        self._updateLinkVisibility();
    }

    _updateLinkVisibility() {
        const self = this;

        const show = (target) => {
            document.getElementById(target).style.display = "inline-block";
        };

        const hide = (target) => {
            document.getElementById(target).style.display = "none";
        };

        if (self._step == 0) {
            hide("back-link-holder");
            show("next-link-holder");
            show("skip-intro-link-holder");
        } else if (self._step == STEP_TEXTS.length - 1) {
            show("back-link-holder");
            show("next-link-holder");
            hide("skip-intro-link-holder");
        } else {
            show("back-link-holder");
            hide("next-link-holder");
            hide("skip-intro-link-holder");
        }
    }

}