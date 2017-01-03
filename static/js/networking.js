
function get(url, cb) {
    $.ajax({
        url: url,
        type: 'GET',
        error: function(xhr, text, error) {
            if(xhr && xhr.responseText) {
                cb(null, xhr.responseText);
            } else if(xhr && xhr.statusText) {
                cb(null, xhr.statusText);
            } else {
                cb(null, error);
            }
        },
        success: function(response, status, xhr) {
            if(response.status === 'error') {
                cb(null, response.error);
            } else {
                cb(response, null);
            }
        }
    });
}

function post(url, data, cb) {
    $.ajax({
        url: url,
        type: 'POST',
        data: JSON.stringify(data),
        contentType: 'application/json',
        error: function(xhr, text, error) {
            if(xhr && xhr.responseText) {
                cb(null, xhr.responseText);
            } else if(xhr && xhr.statusText) {
                cb(null, xhr.statusText);
            } else {
                cb(null, error);
            }
        },
        success: function(response, status, xhr) {
            if(response.status === 'error') {
                cb(null, response.error);
            } else {
                cb(response, null);
            }
        }
    });
}