<!doctype html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title></title>
    <meta name="viewport" content="user-scalable=yes, initial-scale=1.0, maximum-scale=2.0, width=device-width">
    <link rel="stylesheet" href="/static/bootstrap/css/bootstrap.min.css">
    <style>
        *, *:before, *:after {
            -moz-box-sizing: border-box;
            -webkit-box-sizing: border-box;
            box-sizing: border-box;
        }
        body {
            margin: 0;
            padding: 0;
            overflow: hidden;
        }
        .header,
        .footer {
            height: 60px;
            background: #ccc;
            position: fixed;
            width: 100%;
            box-shadow: 0 0px 5px rgba(0, 0, 0, 0.5);
            z-index: 100;
        }
        .footer {
            bottom: 0px;
        }
        .content {
            padding: 60px 0;
            height: 100%;
        }
        html, body,
        .rgb {
            height: 100%;
        }
        .rgb .hue,
        .rgb .sat,
        .rgb .vib,
        #current-temp,
        .target {
            width: 33%;
            height: 100%;
            float: left;
        }
        .handle {
            width: 60%;
            margin: 0 20%;
            text-align: center;
            height: 30px;
            background: #ccc;
            border-radius: 20px;
            background: -moz-linear-gradient(
                top,
                #ccc 0%,
                #999);
            background: -webkit-gradient(
                linear, left top, left bottom,
                from(#ccc),
                to(#999));
            box-shadow: 0px 0px 2px rgba(0, 0, 0, 0.3);
        }
        .rgb .hue,
        .rgb .sat {
            margin-right: 0.5%;
        }
        .current-temp-text {
            font-size: 22px;
        }
    </style>
</head>
<body>
    <div class="navbar navbar-default navbar-fixed-top">
        <div class="container-fluid">
            <div class="navbar-header">
            </div>
        </div>
        <div class="collapse navbar-collapse" id="top">
        </div>
    </div>
    <div class="content">
        <div class="rgb">
            <div id="current-temp">
            </div>
            <div class="target">
                <div class="handle"></div>
            </div>
            <div class="vib">
            </div>
        </div>
    </div>
    <div class="navbar navbar-default navbar-fixed-bottom">
        <div class="container-fluid">
            <div class="row">
                <div class="col-xs-6">
                    <button class="btn btn-default navbar-btn btn-block">Off</button>
                </div>
                <div class="col-xs-6">
                </div>
            </div>
        </div>
        <div class="collapse navbar-collapse" id="bottom">
        </div>
    </div>

    <script src="/static/color-conversion-algorithms.js"></script>
    <script src="/static/jquery-2.1.0.min.js"></script>
    <script src="/static/draggabilly.pkgd.min.js"></script>
    <script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
    <script src="/static/bootstrap/js/bootstrap.min.js"></script>
    <script>
    $(document).ready(function() {
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
        }
        ws.onmessage = function(evt) {
            data = JSON.parse(evt.data);
        }
        ws.onclose = function(evt) {
            console.log('WebSocket connection closed.');
        }

        var currenttemp = {{ ctx['thermostat']['val'] if ctx['thermostat']['val'] else "0" }};
        var targettemp = {{ ctx['thermostat']['target'] }};
        var bounds = {
            top: 85,
            bot: 50
        }
        var curperc = (currenttemp - bounds.bot) / (bounds.top - bounds.bot);

        var h = $("#current-temp").innerHeight();
        var currentTempContainer = d3.select("#current-temp")
        .append("svg")
            .attr("width", $("#current-temp").innerWidth())
            .attr("height", h);

        var currentTempBar = currentTempContainer.append("rect")
            .attr("width", $("#current-temp").innerWidth())
            .attr("height", 0)
            .attr("y", h)
            .attr("fill", "hsl(240, 100%, 50%)");

        var currentTempText = currentTempContainer.append("text")
            .attr("text-anchor", "middle")
            .attr("class", "current-temp-text")
            .attr("height", 20)
            .attr("y", h)
            .attr("x", $("#current-temp").innerWidth() / 2);

        currentTempText.transition()
            .delay(100)
            .duration(400)
                .attr("y", function() {
                    var bary = h - (curperc * h);
                    if (bary < (h / 2)) {
                        return bary + 25;
                    } else {
                        return bary - 15;
                    }
                })
                .tween("text", function(d) {
                    var i = d3.interpolate(this.height, d);
                    return function(t) {
                        this.textContent = Math.round(bounds.bot + (t * (currenttemp - bounds.bot)));
                    };
                });
        currentTempBar.transition()
            .delay(100)
            .duration(400)
                .attr("height", Math.round(curperc * h))
                .attr("y", h - Math.round(curperc * h))
                .attr("fill", "hsl(" + (240 + 120 * curperc) + ", 100%, 50%)");

        var sliderheight = parseFloat($('.target').innerHeight());
        var tarperc = 1 - (targettemp - bounds.bot) / (bounds.top - bounds.bot);
        $('.target .handle').css('top', tarperc * (sliderheight - 30));
        var $target = $('.target');
        function settarget() {
            $('.target .handle').text(Math.round(targettemp));
        }
        settarget();
        targethandle = new Draggabilly($target.find(".handle").get(0), {
            axis: 'y',
            containment: '.target'
        });
        targethandle.on('dragMove', function(instance, e, pointer) {
            targettemp = bounds.bot + (1 - (instance.position.y / (sliderheight - 30))) * (bounds.top - bounds.bot);
            ws.send(JSON.stringify({
                target: "thermostat",
                action: "set",
                value: targettemp
            }));
            settarget();
        });
    });
    </script>
</body>
</html>
