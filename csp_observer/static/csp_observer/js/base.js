function getBaseUrl() {
    return window.location.origin + window.location.pathname;
}

function checkRuleUpdate() {
    var apiPostUrl = getBaseUrl() + 'update/rules/';
    var responseDiv = $('#rule-update-response');
    responseDiv.addClass('alert-info');
    responseDiv.text("Checking for updates...");
    responseDiv.show();
    $.ajax({
        url: apiPostUrl,
        type: 'post',
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function(data) {
            responseDiv.removeClass('alert-info');
            if (data.status === 'ok') {
                responseDiv.addClass('alert-success');
                responseDiv.text(data.message + " Reloading Page...");
                responseDiv.show();
                setTimeout(function() {
                    location.reload();
                }, 3000);
            } else {
                responseDiv.addClass('alert-warning');
                responseDiv.text(data.message);
                responseDiv.show();
            }
        }
    })
}

function deleteCustomRule(ruleId) {
    var apiPostUrl = getBaseUrl() + 'rule/' + ruleId + '/delete';
    $.ajax({
        url: apiPostUrl,
        type: 'post',
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function(data) {
            if (data.status === 'ok') {
                alert(data.message)
            } else {
                alert("An error occurred deleting rule " + ruleId + ":\n\n" + data.message)
            }
            location.reload();
        }
    })
}

function shareSessionData(sessionId) {
    var apiPostUrl = shareSessionUrl;
    var responseDiv = $('#share-data-response');
    responseDiv.addClass('alert-info');
    responseDiv.text("Submitting data...");
    responseDiv.show();
    $.ajax({
        url: apiPostUrl,
        type: 'post',
        headers: {
            'X-CSRFToken': csrfToken
        },
        success: function(data) {
            responseDiv.removeClass('alert-info');
            if (data.status === 'ok') {
                responseDiv.addClass('alert-success');
                responseDiv.text(data.message);
                responseDiv.show();
            } else {
                responseDiv.addClass('alert-warning');
                responseDiv.text(data.message);
                responseDiv.show();
            }
        }
    })
}