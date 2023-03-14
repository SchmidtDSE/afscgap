const STEP_TEXTS = [
    "Hello! This visualization explores data from the NOAA AFSC GAP surveys in and around Alaska. A guided intro is available (click Next >>) or click Skip Intro if you are a returning user.",
    "This is a map of the Gulf of Alaska and these squares show areas where a survey has been taken to determine which fish are present.",
    "For example, these are haul reports for the economically important Pacific cod species. This is in terms of \"catch per unit effort\" or, in other words, weight of cod caught during a survey relative to area surveyed in kilograms per hectare.",
    "Contrast this with the cod numbers from 2021 and note that the catches have gotten smaller, espeically around Kodiak Island in the middle. For many \"hauls\" in the same area, surveys caught fewer cod in 2021 compared to 2013.",
    "It turns out that stocks decreased so much that <a href='https://www.npr.org/2019/12/08/785634169/alaska-cod-fishery-closes-and-industry-braces-for-ripple-effect' target='_blank'>the federal cod fishery closed in 2020</a>. What happened here?",
    "I have a hunch. Let's look at \"The Blob\" warming event which took place 2013-2016. Try changing the date on the second display from 2021 to 2015 to see what was happing mid-event.",
    "Comparing 2013 to 2015, signs of increased pressure start to show up even before the warming event finished. That in mind, I wonder how temperatures changed geographically.",
    "Specifically, let's look at temperature readings taken at the bottom by selecting \"Bottom temperatures\" below.",
    "Now, let's do the same on the other display. Go ahead and select bottom temperatures again in the other dropdown. How did they change between years?",
    "It looks like there may have been some warming in the Gulf of Alaska. I wonder if this was region-wide.",
    "What about the Aleutian Islands? Did the same temperatures appear there? Try putting Gulf of Alaska data in one display and Aleutian Islands data in the other.",
    "Now, let's do 2015 in the Gulf of Alaska and 2014 in the Aleutian Islands. Note that a survey does not happen in every region every year.",
    "The temperatures in some areas of the Gulf of Alaska appear to have been higher at the time of haul compared to the Aleutian Islands.",
    "To better see this, let's overlay the data. On the Gulf of Alaska display, let's put Pacific cod 2013 as Scatter 1 and Pacific cod 2015 as Scatter 2. Then, let's do 2014 and 2016 in the Aleutian Islands.",
    "With these temperature changes displayed, how much did temperature change in each region? How did the catch change in areas of warming? <a href='https://cdnsciencepub.com/doi/full/10.1139/cjfas-2019-0238'>Research suggests that warming matters quite a lot in a region but it's a complex phenomenon impacting spawning habitat</a>. The Gulf of Alaska with widespread warming may have been under more pressure than the Aleutian Islands.",
    "This is a lot of info on Pacific cod. How about walleye pollock? Did that species see something similar happen? Go ahead and explore that species below.",
    "That's it for the intro! Want to learn more about this? See our <a target='_blank' href='https://mybinder.org/v2/gh/SchmidtDSE/afscgap/main?urlpath=/tree/index.ipynb'>example notebook</a>."
];

let allowSpecies2 = true;
let disableResizeRefresh = false;
let disableDeepLink = false;


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
            [],
            ["#display2-species-1"],
            ["#display1-species-1"],
            [".temperature-select-1"],
            [".temperature-select-2"],
            [],
            [".area-select", ".species-type-select"],
            [],
            [],
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
        allowSpecies2 = false;
        disableResizeRefresh = true;
        disableDeepLink = true;
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
        disableResizeRefresh = false;
        disableDeepLink = false;
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

        if (self._stepActions[self._step].indexOf(".species-2") != -1) {
            allowSpecies2 = true;
            disableResizeRefresh = false;
        }

        if (self._step == STEP_TEXTS.length - 1) {
            disableDeepLink = false;
        }

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
            hide("next-link-holder");
            hide("skip-intro-link-holder");
        } else {
            show("back-link-holder");
            show("next-link-holder");
            hide("skip-intro-link-holder");
        }
    }

}