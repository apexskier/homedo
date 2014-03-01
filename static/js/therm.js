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
(function() {
    var days = ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'];

    var months = ['January','February','March','April','May','June','July','August','September','October','November','December'];

    Date.prototype.getMonthName = function() {
        return months[ this.getMonth() ];
    };
    Date.prototype.getDayName = function() {
        return days[ this.getDay() ];
    };
})();
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
    } else if (data.action == "scheduled" && data.status == "success") {
        updateScheduled(data);
    } else {
        console.log('Message recieved');
        console.log(data);
    }
}
ws.onclose = function(evt) {
    console.log('WebSocket connection closed.');
    clearInterval(window.tick);
}

var h = window.innerHeight - 60;
var w = window.innerWidth;
var body = d3.select('body').style('background-color', function() {
    if (currenttemp > targettemp - 2) {
        return 'steelblue';
    } else {
        return '#ff8800';
    }
});
var main = d3.select('#main');
var svg = main.append('svg').attr('height', h).attr('width', w);
svg.append('defs');

var cr = d3.min([w, h]) / 2 - 60;
if (cr > 150) {
    cr = 150;
}
var cy = h / 2 - 30;
var cx = w / 2;

var upx = cx - 30,
    upy = cy - cr - 53;
var up = svg.append('g');
var uprect = up.append('rect')
    .attr('x', upx)
    .attr('y', upy)
    .attr('height', 40)
    .attr('width', 60)
    .attr('rx', 5)
    .attr('ry', 5)
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .attr('fill', 'transparent');
var uptext = up.append('text')
    .attr('class', 'text')
    .attr('x', upx + 30)
    .attr('y', upy + 30)
    .text('Up')
    .style('font-size', 28)
    .attr('text-anchor', 'middle');

var downx = cx - 45,
    downy = cy + cr + 13;
var down = svg.append('g');
var downrect = down.append('rect')
    .attr('x', downx)
    .attr('y', downy)
    .attr('height', 40)
    .attr('width', 90)
    .attr('rx', 5)
    .attr('ry', 5)
    .attr('stroke', '#fff')
    .attr('stroke-width', 2)
    .attr('fill', 'transparent');
var downtext = down.append('text')
    .attr('class', 'text')
    .attr('x', downx + 45)
    .attr('y', downy + 30)
    .text('Down')
    .style('font-size', 28)
    .attr('text-anchor', 'middle');

var circle = svg.append('g');
circle.append('circle')
    .attr('class', 'circle')
    .attr('r', cr)
    .attr('cx', cx)
    .attr('cy', cy)
    .attr('fill', 'transparent');
var t = circle.append('text')
    .attr('class', 'text tar')
    .attr('x', cx)
    .attr('y', cy + (cr * .2))
    .attr('text-anchor', 'middle');
var c = circle.append('text')
    .attr('class', 'text current')
    .attr('x', cx)
    .attr('y', cy + (cr * .55))
    .attr('text-anchor', 'middle');

var s = svg.append('text')
    .attr('class', 'schedule text')
    .attr('x', cx)
    .attr('y', cy + cr + 90)
    .attr('text-anchor', 'middle');

var tarfillclip = svg.select('defs').append('clipPath')
    .attr('id', 'tarfillclip')
    .append('rect')
    .attr('x', cx - cr)
    .attr('y', cy + cr)
    .attr('width', cr * 2)
    .attr('height', 0);
var tarfill = circle.append('circle')
    .attr('r', cr - 12)
    .attr('cx', cx)
    .attr('cy', cy)
    .attr('fill', 'transparent')
    .attr('stroke', '#fff')
    .attr('clip-path', "url(#tarfillclip)")
    .attr('stroke-width', 2);

var fillclip = svg.select('defs').append('clipPath')
    .attr('id', 'fillclip')
    .append('rect')
    .attr('x', cx - cr)
    .attr('y', cy + cr)
    .attr('width', cr * 2)
    .attr('height', 0);
var fill = circle.append('circle')
    .attr('r', cr - 6)
    .attr('cx', cx)
    .attr('cy', cy)
    .attr('fill', 'transparent')
    .attr('stroke', '#fff')
    .attr('clip-path', "url(#fillclip)")
    .attr('stroke-width', 4);

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
    c.text("Currently " + Math.round(currenttemp) + "°");
}
function updateTargetVis(newtemp) {
    if (newtemp > bounds.top) {
        newtemp = bounds.top;
    } else if (newtemp < bounds.bot) {
        newtemp = bounds.bot;
    }
    targettemp = newtemp;
    tarperc = (targettemp - bounds.bot) / bounds.range;

    tarfillclip.transition()
        .duration(400)
        .attr('y', cy - cr + (2 * cr) * (1 - tarperc))
        .attr('height', (cr * 2) * (tarperc));
    t.text(Math.round(targettemp));
}
function updateTarget(newtemp) {
    if (newtemp != targettemp) {
        updateTargetVis(newtemp);
        ws.send(JSON.stringify({
            target: "therm",
            action: "set",
            val: targettemp
        }));
    } else {
        updateTargetVis(newtemp);
    }
}
function updateStatus(st) {
    console.log(st);
    body.transition()
        .duration(400)
        .style('background-color', function() {
            if (st) {
                return '#ff8800';
            } else {
                return 'steelblue';
            }
        });
}
function updateScheduled(data) {
    d = new Date(data.nexttime);
    now = new Date();
    dstr = "";
    if (now.getDayName() != d.getDayName()) {
        dstr += "on " + d.getDayName().slice(0, 3) + " ";
    }
    dstr += "at " + d.getHours() % 12 + ":" + d.getMinutes() + " " + ((d.getHours() > 12) ? "pm" : "am");
    s.text("Setting to " + Math.round(data.val) + "° " + dstr + ".");
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
    circle.on('touchend', hittarget).on('click', hittarget);
    function hitup(d, i) {
        updateTarget(targettemp + 1);
        d3.event.preventDefault();
        uprect.attr('fill', 'transparent').attr('stroke', '#fff');
        uptext.style('fill', '#fff');
    };
    function activeup(d, i) {
        uprect.attr('fill', '#fff').attr('stroke', 'steelblue');
        uptext.style('fill', 'steelblue');
    };
    up.on('click', hitup).on('touchend', hitup);
    up.on('mousedown', activeup).on('touchstart', activeup);
    function hitdown(d, i) {
        updateTarget(targettemp - 1);
        d3.event.preventDefault();
        downrect.attr('fill', 'transparent').attr('stroke', '#fff');
        downtext.style('fill', '#fff');
    };
    function activedown(d, i) {
        downrect.attr('fill', '#fff').attr('stroke', 'steelblue');
        downtext.style('fill', 'steelblue');
    };
    down.on('click', hitdown).on('touchend', hitdown);
    down.on('mousedown', activedown).on('touchstart', activedown);

    var activetouch = false;
    svg.on('touchstart', function() {
        activetouch = d3.touches(this)[0];
    });
}
