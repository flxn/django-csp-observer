function CSPObserverUserInterface(options) {
    this.sessionId = options.sessionId;
    if (!this.sessionId) {
        console.log("Clientui could not be initialized: No session passed");
        return;
    }
    this.visibility = options.visibility || 'always';
    this.resultUri = options.resultUri;
    if (!this.resultUri) {
        console.log("Clientui could not be initialized: No result URI passed");
        return;
    }
    this.detailpageUri = options.detailpageUri;
    if (!this.detailpageUri) {
        console.log("Clientui could not be initialized: No detail URI passed");
        return;
    }
    this.checkTimeout = 10 * 1000;
    this.container = document.getElementById('cspo-clientui');
    this.iconSpinner = document.getElementById('cspo-icon-spinner');
    this.iconCheck = document.getElementById('cspo-icon-check');
    this.iconAlert = document.getElementById('cspo-icon-alert');
    this.textStatusMessage = document.getElementById('cspo-status-message');

    return this;
}

CSPObserverUserInterface.prototype.init = function() {
    this.container.querySelector('.close').addEventListener('click', (function() {
        this.container.style.display = 'none';
    }).bind(this), false);
    
    if (this.visibility === 'always') {
        this.container.classList.add('visible')
    }

    this.setStatusScanning();

    this.container.querySelector('.spoiler').classList.add('hidden');
    this.container.addEventListener("mouseenter", (e) => { 
        this.container.querySelector('.spoiler').classList.remove('hidden')
    });

    this.container.addEventListener("mouseleave", (e) => { 
        this.container.querySelector('.spoiler').classList.add('hidden')
    });

    setTimeout(() => {
        this.checkResult();
    }, this.checkTimeout);
}

CSPObserverUserInterface.prototype.checkResult = function() {
    fetch(this.resultUri)
    .then(response => response.json())
    .then(data => {
        if (data.length > 0) {
            this.setStatusWarning(data.length)
        } else {
            this.setStatusGood()
        
        }
    }).catch(error => {
        console.error("Error fetching result data:", error);
    });
}

CSPObserverUserInterface.prototype.setStatusScanning = function () {
    this.showSpinnerIcon();
    this.textStatusMessage.textContent = "Observing browser behavior...";
}

CSPObserverUserInterface.prototype.setStatusGood = function() {
    this.showCheckIcon();
    this.textStatusMessage.textContent = "No problems detected.";
    setTimeout(() => {
        this.container.style.display = 'none';
    }, 3000)
}

CSPObserverUserInterface.prototype.setStatusWarning = function(numReports) {
    if (this.visibility === 'minimized') {
        this.container.classList.add('visible')
    }
    this.showAlertIcon();
    var problems = numReports === 1 ? 'problem' : 'problems';
    var content = "Detected " + numReports + " " + problems + "!";
    content += '<br\><a href="' + this.detailpageUri + '" target="_blank">Click to learn more.</a>'
    this.textStatusMessage.style.lineHeight = 'inherit';
    this.textStatusMessage.innerHTML = content;
}

CSPObserverUserInterface.prototype.showCheckIcon = function() {
    this.iconSpinner.classList.remove('visible');
    this.iconCheck.classList.add('visible');
    this.iconAlert.classList.remove('visible');
}

CSPObserverUserInterface.prototype.showAlertIcon = function() {
    this.iconSpinner.classList.remove('visible');
    this.iconCheck.classList.remove('visible');
    this.iconAlert.classList.add('visible');
}

CSPObserverUserInterface.prototype.showSpinnerIcon = function() {
    this.iconSpinner.classList.add('visible');
    this.iconCheck.classList.remove('visible');
    this.iconAlert.classList.remove('visible');
}


window.CSPObserverUserInterface = CSPObserverUserInterface;