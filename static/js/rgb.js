if (!window.WebSocket) {
    if (window.MozWebSocket) {
        window.WebSocket = window.MozWebSocket;
    } else {
        console.log("No websockets. :()");
    }
}
var arr = document.URL.split('/');
var result = arr[2];
ws = new WebSocket('ws://' + result + '/control');
ws.onopen = function(evt) {
    console.log('Websocket connection opened.');
    ws.send(JSON.stringify({
        action: 'get',
        target: 'rgb1',
        format: 'hsv'
    }));
}
ws.onmessage = function(evt) {
    data = JSON.parse(evt.data);
    console.log('Message recieved');
    console.log(data);
    if (data.action == "get") {
        rgb1.h = data.val[0];
        rgb1.s = data.val[1];
        rgb1.v = data.val[2];
        console.log('doing');
        hueHandleEl.transition()
            .duration(200)
                .style("top", ((sliderheight - 30) * rgb1.h) + 'px');
        satHandleEl.transition()
            .duration(200)
                .style("top", ((sliderheight - 30) * (1 - rgb1.s)) + 'px');
        vibHandleEl.transition()
            .duration(200)
                .style("top", ((sliderheight - 30) * (1 - rgb1.v)) + 'px');
        setHue();
        setSat();
        setVib();
        setVis();
        console.log('done');
    }
}
ws.onclose = function(evt) {
    console.log('WebSocket connection closed.');
}

rgb1.hsl = function() {
    return hsvToHsl(rgb1.h, rgb1.s, rgb1.v)
}

function hslToHsv(h, s, l) {
    var _rgb = hslToRgb(h, s, l)
    return rgbToHsv(_rgb[0], _rgb[1], _rgb[2]);
}
function hsvToHsl(h, s, v) {
    var _rgb = hsvToRgb(h, s, v)
    return rgbToHsl(_rgb[0], _rgb[1], _rgb[2]);
}


var hueEl = d3.select('.hue .inner');
sliderheight = parseFloat(hueEl.style('height'));
function setHue() {
    var col = rgb1.hsl();
    var s = 50 + (rgb1.hsl()[1] * 50);
    var l = 25 + (rgb1.hsl()[2] * 50);
    hueEl.style('background-image', "-webkit-linear-gradient(top," +
        "hsl(0, "   + s + "%, " + l + "%) 0%," +
        "hsl(40, "  + s + "%, " + l + "%) 11.1111%," +
        "hsl(80, "  + s + "%, " + l + "%) 22.2222%," +
        "hsl(120, " + s + "%, " + l + "%) 33.3333%," +
        "hsl(160, " + s + "%, " + l + "%) 44.4444%," +
        "hsl(200, " + s + "%, " + l + "%) 55.5556%," +
        "hsl(240, " + s + "%, " + l + "%) 66.6667%," +
        "hsl(280, " + s + "%, " + l + "%) 77.7778%," +
        "hsl(320, " + s + "%, " + l + "%) 88.8889%," +
        "hsl(360, " + s + "%, " + l + "%) 100%)");
}
setHue();
var hueHandleEl = hueEl.select(".handle").style('top', '0px').style('display', 'block');
hueHandleEl.data(function() {
    return [rgb1.h]
});
hueHandleEl.transition()
    .duration(200)
        .style("top", ((sliderheight - 30) * rgb1.h) + 'px');
huehandle = new Draggabilly(hueHandleEl[0][0], {
    axis: 'y',
    containment: '.hue .inner'
});
huehandle.on('dragMove', function(instance, e, pointer) {
    //                                                                  v handle height
    rgb1.h = instance.position.y / (sliderheight - 30);
    setSat();
    setVib();
    setVis();
    sendSet();
});

var satEl = d3.select('.sat .inner');
function setSat() {
    var fulls = hsvToHsl(rgb1.h, 1, rgb1.v);
    var lows = hsvToHsl(rgb1.h, 0, rgb1.v);
    satEl.style('background-image', "-webkit-linear-gradient(top," +
        "hsl(" + (fulls[0] * 360) + ", 100%, " + (fulls[2] * 100) + "%) 0%," +
        "hsl(" + (lows[0]  * 360) + ", 0%, "   + (lows[2]  * 100) + "%) 100%)");
}
setSat();
var satHandleEl = satEl.select(".handle").style("top", ((sliderheight - 30) * (1 - rgb1.s)) + 'px').style('display', 'block');
var sathandle = new Draggabilly(".sat .handle", {
    axis: 'y',
    containment: '.sat .inner'
});
sathandle.on('dragMove', function(instance, e, pointer) {
    rgb1.s = 1 - (instance.position.y / (sliderheight - 30));
    setHue();
    setVib();
    setVis();
    sendSet();
});

var vibEl = d3.select('.vib .inner');
function setVib() {
    var fulls = hsvToHsl(rgb1.h, rgb1.s, 1);
    var lows = hsvToHsl(rgb1.h, rgb1.s, 0);
    vibEl.style('background-image', "-webkit-linear-gradient(top," +
        "hsl(" + (fulls[0] * 360) + ", " + (fulls[1] * 100) + "%, " + (fulls[2] * 100) + "%) 0%," +
        "hsl(" + (lows[0]  * 360) + ", " + (lows[1]  * 100) + "%, " + (lows[2]  * 100) + "%) 100%)");
}
setVib();
console.log(rgb1);
var vibHandleEl = vibEl.select(".handle").style("top", ((sliderheight - 30) * (1 - rgb1.v)) + 'px').style('display', 'block');
var vibhandle = new Draggabilly('.vib .handle', {
    axis: 'y',
    containment: '.vib .inner'
});
vibhandle.on('dragMove', function(instance, e, pointer) {
    rgb1.v = 1 - (instance.position.y / (sliderheight - 30));
    setHue();
    setSat();
    setVis();
    sendSet();
});

var bottomEl = d3.select('#bottom');
function setVis() {
    col = rgb1.hsl();
    bottomEl.style('background-color', "hsl(" +
        (col[0] * 360) + ", " +
        (col[1] * 100) + "%, " +
        (col[2] * 100) + "%)");
}
function sendSet() {
    ws.send(JSON.stringify({
        target: "rgb1",
        action: "set",
        format: "hsv",
        val: [
            rgb1.h,
            rgb1.s,
            rgb1.v
        ]
    }));
}
setVis();

d3.select('#off').on('click', function(e) {
    rgb1.v = 0;
    rgb1.h = 0;
    rgb1.s = 0;
    hueHandleEl.transition()
        .duration(200)
            .style('top', 0 + 'px');
    satHandleEl.transition()
        .duration(200)
            .style('top', (sliderheight - 30) + 'px');
    vibHandleEl.transition()
        .duration(200)
            .style('top', (sliderheight - 30) + 'px');
    setHue();
    setSat();
    setVib();
    setVis();
    ws.send(JSON.stringify({
        target: "rgb1",
        action: "off"
    }));
})
