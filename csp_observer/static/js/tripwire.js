var scanInterval = 5000;
var scanTimeout = 30000;
var timer = null;
var sessionId = null;
var policy = null;
var debug = true;
var checkedTags = [];

function PolicyParser(policyString) {
    this.policy = policyString.split(/;/);
    this.directives = {};

    // parse directives
    for (var i = 0; i < this.policy.length; i++) {
        var directive = this.policy[i].trim();
        var parts = directive.split(/\s+/);
        var name = parts[0].trim();
        var value = parts[1].trim();
        value = value.replace(/^[\"\']+|[\"\']+$/g, "");
        this.directives[name] = value;
    }

    return this;
}

PolicyParser.prototype.checkElementAllowed = function (htmlElement) {
    var directive = this.directives['default-src'];

    // extract source path
    // TODO: think about edge cases, maybe too generic right now
    var sourcePath = htmlElement.getAttribute('src')
    if (!sourcePath) {
        sourcePath = htmlElement.getAttribute('href')
    }
    if (!sourcePath) {
        return true;
    }

    switch (htmlElement.tagName.toLowerCase()) {
        case 'script':
            if (Object.keys(this.directives).indexOf('script-src') !== -1) {
                directive = this.directives['script-src'];
            }
            break;
        case 'img':
            if (Object.keys(this.directives).indexOf('img-src') !== -1) {
                directive = this.directives['img-src'];
            }
            break;
        case 'link':
            // TODO: there are multiple types of link tags that should also be handled
            if (htmlElement.getAttribute('rel') === 'stylesheet'
                && Object.keys(this.directives).indexOf('style-src') !== -1) {
                directive = this.directives['style-src'];
            }
            break;
        case 'audio':
        case 'video':
            if (Object.keys(this.directives).indexOf('media-src') !== -1) {
                directive = this.directives['media-src'];
            }
            break;
        case 'iframe':
            if (Object.keys(this.directives).indexOf('frame-src') !== -1) {
                directive = this.directives['frame-src'];
            }
            break;
        case 'embed':
        case 'object':
        case 'applet':
            if (Object.keys(this.directives).indexOf('object-src') !== -1) {
                directive = this.directives['object-src'];
            }
            break;
        default:
            return true;
    }

    // TODO: implement better path matching
    if (directive === '*') {
        return true;
    } else if (directive === 'self') {
        return (sourcePath[0] === '/' || sourcePath.indexOf(location.href) !== -1)
    } else {
        return sourcePath.indexOf(directive) !== -1
    }

}

function init() {
    sessionId = document.currentScript.getAttribute('data-session');
    if (!sessionId) {
        console.log("Tripwire could not be initialized: No session passed");
        return;
    }

    policy = document.currentScript.getAttribute('data-policy');
    if (!policy) {
        console.log("Tripwire could not be initialized: No policy passed");
        return;
    }
    var policyString = atob(policy);
    var policyParser = new PolicyParser(policyString);

    if (debug) console.log("### Tripwire loaded ###");
    if (debug) console.log("CSP Observer Session ID:", sessionId);
    if (debug) console.log("Scan Interval:", scanInterval, "ms");
    if (debug) console.log("Active Policy:", policyString);

    timer = setInterval(function () {
        // iterate through all elements on the page
        var elements = document.getElementsByTagName('*');
        for (var i = 0; i < elements.length; i++) {
            var allowed = policyParser.checkElementAllowed(elements[i]);
            if (!allowed) {
                if (debug) console.log("### Tripwire activated ###")
                if (debug) console.log(elements[i])
                if (debug) console.log("##########################")
            }
        }
    }, scanInterval);

    // stop scan after scanTimeout milliseconds
    setTimeout(function () {
        clearInterval(timer);
    }, scanTimeout);
}

init();