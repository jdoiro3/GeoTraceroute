
const CAMERA_SPEED = 2000;
const CAMERA_ALTITUDE = .8


function scroll(){
    var objDiv = document.getElementById("terminal");
    objDiv.scrollTop = objDiv.scrollHeight;
}


function tracerouteGlobe(pos) {
    // remove previous data
    globe.arcsData([]);
    let labelsData = [];
    $('#terminal').empty();
    // add home
    labelsData.push({
        latitude: pos.coords.latitude,
        longitude: pos.coords.longitude,
        name: 'Home',
        info: {city: 'Home'}
    })
    globe.labelsData(labelsData);
    globe.pointOfView({lat: pos.coords.latitude, lng: pos.coords.longitude, altitude: CAMERA_ALTITUDE }, CAMERA_SPEED);

    var socket = new WebSocket("ws://localhost:8888/ws");

    socket.onopen = function(e) {
        let host = document.getElementById('host').value;
        socket.send(`{"data": {
            "host": "${host}",
            "token": "${API_TOKEN}"
        }}`);
    };

    socket.onmessage = function(event) {
        let data = JSON.parse(event.data);
        // print message to terminal output on page
        if (data.type === "output" || data.type === "input") {
            let output = `<p class=" terminal--${data.type} ">${data.msg}</p>`;
            $('#terminal').append(output);
            scroll();
        // it's a geo message
        } else {
            if (!data.msg.bogon) {
                let arcsData = globe.arcsData();
                let labelsData = globe.labelsData();
                let last_location = labelsData.at(-1);
                let new_loc_lat = parseFloat(data.msg.loc.split(",")[0]);
                let new_loc_lng = parseFloat(data.msg.loc.split(",")[1]);
                arcsData.push({
                    startLat: last_location.latitude,
                    startLng: last_location.longitude,
                    endLat: new_loc_lat,
                    endLng: new_loc_lng,
                    color: 'white',
                    name: `${last_location.name} -> ${data.msg.city}`
                });
                labelsData.push({
                    latitude: new_loc_lat,
                    longitude: new_loc_lng,
                    name: data.msg.city,
                    info: data.msg
                })
                globe.arcsData(arcsData);
                globe.labelsData(labelsData);
                globe.pointOfView({lat: new_loc_lat, lng: new_loc_lng, altitude: CAMERA_ALTITUDE }, CAMERA_SPEED);
            }
        }
    };

    socket.onerror = function(event) {
        console.log(event);
    };

}


function error(err) {
  console.warn(`ERROR(${err.code}): ${err.message}`);
}

function main() {
    let options = {
      enableHighAccuracy: true,
      timeout: 5000,
      maximumAge: 0
    };
    navigator.geolocation.getCurrentPosition(tracerouteGlobe, error, options);
}


// prompt user for api token
const API_TOKEN = token;
const globe = Globe()
    .globeImageUrl("https://unpkg.com/three-globe@2.18.11/example/img/earth-blue-marble.jpg")
    .bumpImageUrl("https://unpkg.com/three-globe/example/img/earth-topology.png")
    .backgroundImageUrl("https://unpkg.com/three-globe@2.18.11/example/img/night-sky.png")
    .arcColor('color')
    .arcLabel(d => null)
    .arcDashLength(0.1)
    .arcDashGap(1)
    .arcDashAnimateTime(1000)
    .arcsTransitionDuration(100)
    .labelLat(d => d.latitude)
    .labelLng(d => d.longitude)
    .labelText(d => d.info.city)
    .labelDotRadius(d => .1)
    .labelColor(() => 'rgba(255, 165, 0, 0.75)')
    .labelResolution(2)
    .labelLabel(d => `
        <div><b>IP: ${d.info.ip}</b></div>
        <div>ORG: ${d.info.org}</div>`
    )
    (document.getElementById('globeViz'))

globe.onZoom(({ lat, lng, altitude }) => {
    globe.labelSize(d => .5*altitude);
})
globe.labelSize(d => {
    let altitude = globe.pointOfView().altitude;
    return .5*altitude;
})