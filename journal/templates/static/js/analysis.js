
async function sendConnectionData (url, data) {
    post(url, JSON.stringify(data), callback = (response) => {
        console.log(response);
    });
}

async function saveData (url) {
    let connection_data = {
        'user_id': null,
        'language': navigator.language,
        'user_agent': navigator.userAgent,
        'is_mobile': navigator.userAgentData.mobile,
        'platform': navigator.userAgentData.platform,
        'screen_width': screen.width,
        'screen_height': screen.height,
        'vendor': navigator.vendor,
        'latitude': null,
        'longitude': null
    };
    
    // await (await fetch('https://api.ipify.org?format=json')).json(); // To get the IP 
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                connection_data['latitude'] = position.coords.latitude;
                connection_data['longitude'] = position.coords.longitude;
                sendConnectionData(url, connection_data);
            },
            (position) => {
                $.ajax({
                    dataType: "json",
                    url: "https://ipapi.co/json/",
                    success: function (data) {
                        connection_data['latitude'] = data.latitude;
                        connection_data['longitude'] = data.longitude;
                        sendConnectionData(url, connection_data);
                    }
                });
            });
    } else {
        $.ajax({
            dataType: "json",
            url: "https://ipapi.co/json/",
            success: function (data) {
                connection_data['latitude'] = data.latitude;
                connection_data['longitude'] = data.longitude;
                sendConnectionData(url, connection_data);
            }
        });
    }
}