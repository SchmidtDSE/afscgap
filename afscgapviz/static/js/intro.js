const STEP_TEXTS = [
    "Hello! This visualization explores data from the NOAA AFSC GAP surveys in and around Alaska. A guided intro is available (click Next >>) or click Skip Intro if you are a returning user.",
    "We will walk through an example problem together: what happened to the cod stocks in Alaska?",
    "This is a map of the Gulf of Alaska and these squares show areas where a survey has been taken to determine which fish are present.",
    "For example, these are haul reports for the economically important Pacific cod species. This is in terms of \"catch per unit effort\" or, in other words, weight of cod caught during a survey relative to area surveyed in kilograms per hectare.",
    "Contrast this with the cod numbers from 2021 and note that the catches have gotten smaller, espeically around Kodiak Island in the middle. For many \"hauls\" in the same area, surveys caught fewer cod in 2021 compared to 2013.",
    "It turns out that stocks decreased so much that <a href='https://www.npr.org/2019/12/08/785634169/alaska-cod-fishery-closes-and-industry-braces-for-ripple-effect' target='_blank'>the federal cod fishery closed in 2020</a>. What happened here? Let's find out! Click \"Next\" below.",
    "I have a hunch: \"The Blob\" warming event which took place roughly from 2013 to 2016. Let's stick with Pacific cod for now but try changing the date on the second display from 2021 to 2015 to see what was happing mid-event.",
    "Comparing 2013, signs of increased pressure start to show up even in 2015. That in mind, I wonder how temperatures changed geographically.",
    "Specifically, let's look at temperature readings taken at the bottom by selecting \"Bottom temperatures\" for the first display below. We will add it to the other display in a moment.",
    "Now, let's do the same on the other display. Go ahead and select bottom temperatures again in the other dropdown. How did they change between years?",
    "It looks like there may have been some warming in the Gulf of Alaska. I wonder if this was region-wide?",
    "What about the Aleutian Islands? Did the same temperatures appear there? Try putting Gulf of Alaska data in one display and Aleutian Islands data in the other. Again, let's stick with Pacific cod for now.",
    "Specifically, go ahead and select 2015 in the Gulf of Alaska and 2014 in the Aleutian Islands (Pacific cod in both). Note that a survey does not happen in every region every year.",
    "The temperatures in some areas of the Gulf of Alaska appear to have been higher at the time of haul compared to the Aleutian Islands.",
    "Was this also true right before The Blob? Let's compare the Gulf of Alaska in 2013 to the Aleutian Islands in 2012.",
    "Looks like it! There are areas with higher temperatures in the Gulf of Alaska compared to the Aleutian Islands beforehand as well.",
    "That in mind, to better see what happened with The Blob, let's overlay the data. On the Gulf of Alaska display, let's put Pacific cod 2013 as Scatter 1 and Pacific cod 2015 as Scatter 2. Then, let's do 2014 and 2016 in the Aleutian Islands. Note that the year selector will appear after selecting a species.",
    "With these temperature deltas visualized, how much did temperature change in each region? How did the catch change in areas of warming?",
    "For Pacific cod, <a href='https://cdnsciencepub.com/doi/full/10.1139/cjfas-2019-0238'>research suggests that warming matters quite a lot in a region but it's a complex phenomenon impacting spawning habitat</a>. The Gulf of Alaska with widespread warming may have been under more pressure than the Aleutian Islands.",
    "This is a lot of info on Pacific cod. How about walleye pollock? Did that species see something similar happen? Go ahead and explore that species below.",
    "That's it for the intro! Want to learn more about this? See our <a target='_blank' href='https://mybinder.org/v2/gh/SchmidtDSE/afscgap/main?urlpath=/tree/index.ipynb'>example notebook</a>."
];

const PRESERVE_BOUNDS = ["#display-1", "#display-2", ".viz"];


class Intro {

    constructor() {
        const self = this;
        self._step = 0;

        self._registerCallbacks();

        self._stepActions = [
            [],
            [],
            ["#display-1", ".viz", ".land", ".water"],
            [".fish", ".radius-legend-holder", ".graph-description"],
            ["#display-2"],
            [],
            ["#display2-species-1"],
            ["#display1-species-1"],
            [".temperature-select-1"],
            [".temperature-select-2", ".dynamic-scales-options"],
            [],
            [".area-select", ".species-type-select"],
            [],
            [],
            [],
            [],
            [".species-2"],
            [".download-panel"],
            [],
            [],
            []
        ];

        allowSpecies2 = false;
        disableDeepLink = true;

        self.forceSync();
    }

    isDone() {
        const self = this;
        return self._step == STEP_TEXTS.length - 1;
    }

    forceSync() {
        const self = this;

        document.getElementById("intro-text").innerHTML = STEP_TEXTS[
            self._step
        ];
        d3.select("#intro-links").transition().style("opacity", 1);

        self._stepActions.forEach((actions) => {
            actions.forEach((action) => {
                d3.selectAll(action).attr("originalDisplay", function() {
                    return this.style.display;
                });

                if (PRESERVE_BOUNDS.indexOf(action) == -1) {
                    d3.selectAll(action).style("display", "none");
                }

                d3.selectAll(action).style("opacity", "0");
            });
        });

        for (let i = 0; i <= self._step; i++) {
            self._stepActions[i].forEach((action, i) => {
                d3.selectAll(action).style("display", function() {
                    return this.originalDisplay;
                });
                d3.selectAll(action).transition()
                    .style("opacity", 1);
            });
        }

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
        allowSpecies2 = true;
        disableDeepLink = false;
    }

    _backStep() {
        const self = this;
        self._step--;
        
        self._displayMessage();
        
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
                .delay(i * 200 + 700)
                .style("opacity", 1);
        });

        d3.select("#intro-links")
            .style("display", "none")
            .style("opacity", 0);

        setTimeout(() => {
            d3.select("#intro-links").style("display", "block");
            d3.select("#intro-links").transition().style("opacity", 1);
        }, 200);

        self._displayMessage();

        if (self._stepActions[self._step].indexOf(".species-2") != -1) {
            allowSpecies2 = true;
        }

        if (self.isDone()) {
            disableDeepLink = false;
        }

        self._updateLinkVisibility();
    }

    _displayMessage() {
        const self = this;
        let newText = STEP_TEXTS[self._step];
        console.log(document.documentElement.clientWidth);
        if (self._step == 1) {
            if (document.documentElement.clientWidth < 1100) {
                newText += " Note that this demo works best in a wide window.";
            }
        }
        d3.select("#intro-text").html(newText).style("opacity", 0);
        d3.select("#intro-text").transition().style("opacity", 1);
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
        } else if (self.isDone()) {
            show("back-link-holder");
            hide("next-link-holder");
            hide("skip-intro-link-holder");
        } else {
            show("back-link-holder");
            show("next-link-holder");
            hide("skip-intro-link-holder");
        }
    }

}