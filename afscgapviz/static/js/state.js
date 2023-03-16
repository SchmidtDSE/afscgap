/**
 * Flags which influence the overall visualization behavior.
 * 
 * Flags which influence the overall visualization behavior whose manipulation
 * is often required for assistive features such as the introduction sequence.
 * 
 * @license BSD 3 Clause
 * @author Regents of University of California / The Eric and Wendy Schmidt
 *      Center for Data Science and the Environment at UC Berkeley.
 */

// Flag indicating if the user is allowed to select a second species for a
// display as an overlay. True means that a second species can be selected.
let allowSpecies2 = true;

// Flag indicating if the automatic response to browser size change should be
// enabled / disabled. False means that automatic resize response is enabled.
let disableResizeRefresh = false;

// Flag indicating if the history manipulation (with deep linking) should be
// enabled. False means that the URL will be rewritten as the user changes their
// query with URLs written to browser history.
let disableDeepLink = false;
