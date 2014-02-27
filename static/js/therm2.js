if (!window.WebSocket) {
    if (window.MozWebSocket) {
        window.WebSocket = window.MozWebSocket;
    } else {
        console.log("No websockets. :()");
    }
}
var arr = document.URL.split('/');
bounds.range = bounds.top - bounds.bot;
var result = arr[2];
ws = new WebSocket('ws://' + result + '/control');
var page;
ws.onopen = function(evt) {
    console.log('Websocket connection opened.');
    page = setUp();
    window.tick = setInterval(function() {
        ws.send(JSON.stringify({
            action: 'get',
            target: 'therm'
        }));
        ws.send(JSON.stringify({
            action: 'get_status',
            target: 'therm'
        }));
    }, 10000);
}
ws.onmessage = function(evt) {
    data = JSON.parse(evt.data);
    if (data.action == "get" && data.status == "success") {
        updateTemp(data.val);
    } else if (data.action == "get_status" && data.status == "success") {
        updateStatus(data.val);
    } else {
        console.log('Message recieved');
        console.log(data);
    }
}
ws.onclose = function(evt) {
    console.log('WebSocket connection closed.');
    clearInterval(window.tick);
}

var h = window.innerHeight - 120;
var w = window.innerWidth;
var main = d3.select('#main');
var svg = main.append('svg').attr('height', h).attr('width', w);
svg.append('defs');

var cr = d3.min([w, h]) / 2 - 60;
var cy = h / 2 - 25;

var up = svg.append('circle')
    .attr('cx', w / 2)
    .attr('cy', cy - cr + 5)
    .attr('r', 30)
    .attr('fill', 'grey');
var down = svg.append('circle')
    .attr('cx', w / 2)
    .attr('cy', cy + cr - 5)
    .attr('r', 30)
    .attr('fill', 'grey');

var circle = svg.append('circle')
    .attr('class', 'circle')
    .attr('r', cr)
    .attr('cx', w / 2)
    .attr('cy', cy)
    .attr('stroke', '#fff')
    .attr('fill', function() {
        if (currenttemp > targettemp + 2) {
            return 'steelblue';
        } else {
            return '#ff8800';
        }
    })
    .attr('stroke-width', 2);
var t = svg.append('text')
    .attr('class', 'text tar')
    .attr('x', w / 2)
    .attr('y', cy + (cr * .15))
    .attr('text-anchor', 'middle');
var c = svg.append('text')
    .attr('class', 'text current')
    .attr('x', w / 2)
    .attr('y', cy + (cr * .52))
    .attr('text-anchor', 'middle');

var s = svg.append('text')
    .attr('class', 'schedule')
    .attr('x', w / 2)
    .attr('y', cy + cr + 70)
    .attr('text-anchor', 'middle');

var tarfillclip = svg.select('defs').append('clipPath')
    .attr('id', 'tarfillclip')
    .append('rect')
    .attr('x', w / 2 - cr)
    .attr('y', cy + cr)
    .attr('width', cr * 2)
    .attr('height', 0);
var tarfill = svg.append('circle')
    .attr('r', cr - 12)
    .attr('cx', w / 2)
    .attr('cy', cy)
    .attr('fill', 'transparent')
    .attr('stroke', '#fff')
    .attr('clip-path', "url(#tarfillclip)")
    .attr('stroke-width', 2);

var fillclip = svg.select('defs').append('clipPath')
    .attr('id', 'fillclip')
    .append('rect')
    .attr('x', w / 2 - cr)
    .attr('y', cy + cr)
    .attr('width', cr * 2)
    .attr('height', 0);
var fill = svg.append('circle')
    .attr('r', cr - 6)
    .attr('cx', w / 2)
    .attr('cy', cy)
    .attr('fill', 'transparent')
    .attr('stroke', '#fff')
    .attr('clip-path', "url(#fillclip)")
    .attr('stroke-width', 4);

var eventtarget = svg.append('circle')
    .attr('id', 'eventtarget')
    .attr('r', cr)
    .attr('cx', w / 2)
    .attr('cy', cy)
    .attr('fill', 'transparent');

function updateTemp(newtemp) {
    if (newtemp > bounds.top) {
        newtemp = bounds.top;
    } else if (newtemp < bounds.bot) {
        newtemp = bounds.bot;
    }
    currenttemp = newtemp;
    curperc = (currenttemp - bounds.bot) / bounds.range;

    fillclip.transition()
        .duration(400)
        .attr('y', cy - cr + (2 * cr) * (1 - curperc))
        .attr('height', (cr * 2) * (curperc));
    c.text("Currently " + Math.round(currenttemp));
}
function updateTarget(newtemp) {
    if (newtemp > bounds.top) {
        newtemp = bounds.top;
    } else if (newtemp < bounds.bot) {
        newtemp = bounds.bot;
    }
    targettemp = newtemp;
    tarperc = (targettemp - bounds.bot) / bounds.range;

    ws.send(JSON.stringify({
        target: "therm",
        action: "set",
        val: targettemp
    }));

    tarfillclip.transition()
        .duration(400)
        .attr('y', cy - cr + (2 * cr) * (1 - tarperc))
        .attr('height', (cr * 2) * (tarperc));
    t.text(Math.round(targettemp));
}
function updateStatus(st) {
    console.log(st);
    circle.transition()
        .duration(400)
        .attr('fill', function() {
            if (st) {
                return '#ff8800';
            } else {
                return 'steelblue';
            }
        });
}

function setUp() {
    updateTemp(currenttemp);
    updateTarget(targettemp);
    function hittarget(d, i) {
        var t = d3.mouse(this) || d3.touches(this)[0];
        var ypos = t[1] - (parseFloat(d3.event.target.attributes.cy.value) - parseFloat(d3.event.target.attributes.r.value));
        var newval = ((1 - (ypos / (d3.event.target.attributes.r.value * 2))) * bounds.range) + bounds.bot;
        updateTarget(newval);
        d3.event.preventDefault();
    }
    eventtarget.on('click', hittarget);
    eventtarget.on('touchend', hittarget);
    function hitup(d, i) {
        updateTarget(targettemp + 1);
        d3.event.preventDefault();
    };
    up.on('click', hitup);
    up.on('touchend', hitup);
    function hitdown(d, i) {
        updateTarget(targettemp - 1);
        d3.event.preventDefault();
    };
    down.on('click', hitdown);
    down.on('touchend', hitdown);

    var activetouch = false;
    svg.on('touchstart', function() {
        activetouch = d3.touches(this)[0];
    });
}
