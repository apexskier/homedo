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
var page;
ws.onopen = function(evt) {
    console.log('Websocket connection opened.');
    page = setUp();
    page.showCurrentTemp();
    setInterval(function() {
        ws.send(JSON.stringify({
            action: 'get',
            target: 'therm'
        }));
    }, 10000)
}
ws.onmessage = function(evt) {
    data = JSON.parse(evt.data);
    console.log('Message recieved');
    console.log(data);
    if (data.action == "get" && data.val != null) {
        currenttemp = data.val;
        curperc = (currenttemp - bounds.bot) / (bounds.top - bounds.bot);
        page.showCurrentTemp();
    }
}
ws.onclose = function(evt) {
    console.log('WebSocket connection closed.');
}

function setUp() {
    var currentTempEl = d3.select("#current-temp");
    var h = parseInt(currentTempEl.style('height'));
    var w = parseInt(currentTempEl.style('width')) - 30;
    var currentTempContainer = currentTempEl
        .append("svg")
            .attr("width", '100%')
            .attr("height", h);

    var currentTempBar = currentTempContainer.append("rect")
        .attr("width", 20)
        .attr("height", 30)
        .attr("y", h - 30)
        .attr("x", Math.round(w / 2) - 10)
        .attr("rx", 10)
        .attr("ry", 10)
        .attr("class", "current-temp-bar")
        .attr("fill", "#0088ff");
    var currentTempText = currentTempContainer.append("text")
        .attr("text-anchor", "middle")
        .attr("class", "current-temp-text")
        .attr("height", 20)
        .attr("y", h)
        .attr("x", w / 2 + 38);
    var currentTempHandle = currentTempContainer.append("circle")
        .attr("r", 15)
        .attr("cy", h - 15)
        .attr("cx", Math.round(w / 2))
        .attr("class", "current-temp-handle")
        .attr("fill", "#ccc");

    var targetEl = d3.select('.target')
    var sliderheight = parseFloat(targetEl.style('height'));
    var tarperc = 1 - (targettemp - bounds.bot) / (bounds.top - bounds.bot);
    var targetHandle = targetEl.select('.handle')
        .style('display', 'block')
        .style('top', Math.round(tarperc * (sliderheight - 30)) + 'px')
        .style('opacity', 0);
    targetHandle.transition()
        .delay(100)
        .duration(200)
            .style('opacity', 1)

    function settarget() {
        targetHandle.select('.text').text(Math.round(targettemp));
    }
    settarget();
    targethandle = new Draggabilly(".target .handle", {
        axis: 'y',
        containment: '.target'
    });
    targethandle.on('dragMove', function(instance, e, pointer) {
        targettemp = bounds.bot + (1 - (instance.position.y / (sliderheight - 30))) * (bounds.top - bounds.bot);
        ws.send(JSON.stringify({
            target: "therm",
            action: "set",
            val: targettemp
        }));
        settarget();
    });

    ret = {}
    ret.showCurrentTemp = function() {
        var lasttext = parseInt(currentTempText[0].textContent) || bounds.bot;
        console.log(currentTempText);
        console.log(lasttext);
        currentTempText.transition()
            .duration(400)
                .attr("y", function() {
                    var bary = h - (curperc * h);
                    return bary + 23;
                })
                .tween("text", function(d) {
                    return function(t) {
                        this.textContent = Math.round(lasttext + (t * (currenttemp - bounds.bot)));
                    };
                });
        currentTempBar.transition()
            .duration(400)
                .attr("height", Math.round(curperc * h))
                .attr("y", h - Math.round(curperc * h))
                .attr("fill", function() {
                    r = 255 * curperc;
                    b = 255 - r;
                    hex = "#" + Math.round(r).toString(16) + "88" + Math.round(b).toString(16);
                    return hex;
                });
        currentTempHandle.transition()
            .duration(400)
                .attr("cy", h - Math.round(curperc * h) + 15);
    }
    return ret;
}
