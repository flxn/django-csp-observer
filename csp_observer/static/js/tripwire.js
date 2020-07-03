function PolicyParser(policyString) {
    this.policy = policyString.split(/;/);
    this.directives = {};

    // parse directives
    for (var i = 0; i < this.policy.length; i++) {
        var directive = this.policy[i].trim();
        var parts = directive.split(/\s+/);
        var name = parts[0].trim();
        var value = parts[1].trim();
        // remove leading and trailing quotes from directive values
        value = value.replace(/^[\"\']+|[\"\']+$/g, "");
        this.directives[name] = value;
    }

    return this;
}

PolicyParser.prototype.getViolation = function (htmlElement) {
    var sourcePath = htmlElement.getAttribute('src')
    var matchingDirective = 'default-src';

    switch (htmlElement.tagName.toLowerCase()) {
        case 'script':
            matchingDirective = 'script-src';
            break;
        case 'img':
            matchingDirective = 'img-src';
            break;
        case 'link':
            // TODO: there are multiple types of link tags that should also be handled
            if (htmlElement.getAttribute('rel') === 'stylesheet') {
                matchingDirective = 'style-src'
            }
            sourcePath = htmlElement.getAttribute('href');
            break;
        case 'audio':
        case 'video':
            matchingDirective = 'media-src';
            break;
        case 'iframe':
            matchingDirective = 'frame-src';
            break;
        case 'embed':
        case 'object':
        case 'applet':
            matchingDirective = 'object-src';
            break;
        default:
            return null;
    }

    if (!sourcePath) {
        return null;
    }

    var directive;
    if (Object.keys(this.directives).indexOf(matchingDirective) !== -1) {
        directive = this.directives[matchingDirective];
    } else {
        directive = this.directives['default-src'];
    }

    // TODO: implement better path matching
    if (directive === '*') {
        return null;
    } else if (directive === 'self') {
        if (sourcePath[0] !== '/' && sourcePath.indexOf(location.href) === -1) {
            return {
                source: sourcePath,
                directive: matchingDirective
            };
        } else {
            return null;
        }
    } else if (sourcePath.indexOf(directive) === -1) {
        return {
            source: sourcePath,
            directive: matchingDirective
        };
    } else {
        return null;
    }
}

function Tripwire() {
    this.scanInterval = 5000;
    this.scanTimeout = 30000;
    this.timer = null;
    this.sessionId = null;
    this.reportUri = null;
    this.debug = true;
    this.policyString = "";
    this.reportData = [];
    this.detectedElements = [];

    return this;
}

Tripwire.prototype.init = function () {
    this.sessionId = document.currentScript.getAttribute('data-session');
    if (!this.sessionId) {
        console.log("Tripwire could not be initialized: No session passed");
        return;
    }

    this.reportUri = document.currentScript.getAttribute('data-report-uri');
    if (!this.reportUri) {
        console.log("Tripwire could not be initialized: No report URI passed");
        return;
    } 

    var policy = document.currentScript.getAttribute('data-policy');
    if (!policy) {
        console.log("Tripwire could not be initialized: No policy passed");
        return;
    }
    this.policyString = atob(policy);

    if (this.debug) {
        console.log("### Tripwire loaded ###");
        console.log("CSP Observer Session ID:", this.sessionId);
        console.log("Scan Interval:", this.scanInterval, "ms");
        console.log("Active Policy:", this.policyString);
        console.log("Tripwire Report URI:", this.reportUri);
    }

    // start scan
    this.timer = setInterval(
        (function(self) {
            return function() {
                self.scan();
            }
        })(this), this.scanInterval);

    // stop scan after scanTimeout milliseconds
    setTimeout(
        (function(self) {
            return function() {
                clearTimeout(self.timer);
            }
        })(this), this.scanTimeout);
}

Tripwire.prototype.scan = function () {
    var policyParser = new PolicyParser(this.policyString);
    // iterate through all elements on the page
    var elements = document.getElementsByTagName('*');
    for (var i = 0; i < elements.length; i++) {
        if (this.detectedElements.indexOf(elements[i]) === -1) {
            var violation = policyParser.getViolation(elements[i]);
            if (!!violation) {
                this.detectedElements.push(elements[i]);
                this.reportData.push({
                    'document': location.href,
                    'directive': violation.directive,
                    'source': violation.source
                })
                if (this.debug) {
                    console.log("### Tripwire activated ###");
                    console.log(elements[i]);
                    console.log("##########################");
                }
            }
        }
    }

    this.sendReport();
}

Tripwire.prototype.sendReport = function () {
    var xhr = new XMLHttpRequest();
    xhr.onload = () => {
        if (this.debug) {
            if (xhr.status >= 200 && xhr.status < 300) {
                console.log("Tripwire Violation Report sent successfully");
            } else {
                console.log("Error sending Tripwire Violation Report. Status:", xhr.status);
            }
            
        }
    };

    xhr.open('POST', this.reportUri);
    xhr.setRequestHeader('Content-Type', 'application/json');

    xhr.send(JSON.stringify(this.reportData));
}

var tripwire = new Tripwire();
tripwire.init();