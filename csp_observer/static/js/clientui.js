function CSPObserverUserInterface(options) {
    this.sessionId = options.sessionId;
    if (!this.sessionId) {
        console.log("Clientui could not be initialized: No session passed");
        return;
    }
    this.visibility = options.visibility || 'always';
    this.element = document.getElementById('cspo-clientui');
    return this;
}

CSPObserverUserInterface.prototype.init = function() {
    console.log(this.element)
    this.element.querySelector('.close').addEventListener('click', (function() {
        this.element.style.display = 'none';
    }).bind(this), false);

    if (this.visibility === 'always') {
        this.element.classList.add('visible')
    }
}

window.CSPObserverUserInterface = CSPObserverUserInterface;