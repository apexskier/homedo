<!doctype html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title></title>

    <link rel="stylesheet" href="/static/sldr.dist.css">
    <link rel="stylesheet" href="/static/jquery-minicolors/jquery.minicolors.css">

    <style>
        * {
            box-sizing: border-box;
        }
        input[type="range"] {
            width: 90%;
            margin-left: 5%;
            margin-right: 5%;
        }
        #hue {
            -webkit-appearance: none;
            background-image: -webkit-linear-gradient(left,
                hsl(0, 100%, 50%) 0%,
                hsl(120, 100%, 50%) 33.3333%,
                hsl(240, 100%, 50%) 66.6667%,
                hsl(360, 100%, 50%) 100%);
        }
        input[type="range"]#hue::-webkit-slider-thumb {
            -webkit-appearance: none;
            height: 40px;
            width: 20px;
            background: black;
            border: 2px solid white;
            border-radius: 2px;
        }

        .sldr {
            width: 100%;
            margin: 20px auto;
        }
        .sldr .wrap {
            height: 50px;
        }

        .minicolors {
            margin: 5px auto;
        }

        #thermostat-control {

        }
        #thermostat-control div {
            width: 200px;
            height: 200px;
            border: 2px solid #999;
        }
        #thermostat-control #up {
        }
        #thermostat-control #down {
        }
    </style>
</head>
<body>
    <form>
        <!--<input id="hue" name="hue" type="range" min="0" max="1" step=".003921569" value="{{ ctx['rgb1']['hsv'][0] }}"><br>
        <input id="sat" name="sat" type="range" min="0" max="1" step=".003921569" value="{{ ctx['rgb1']['hsv'][1] }}"><br>
        <input id="light" name="light" type="range" min="0" max="1" step=".003921569" value="{{ ctx['rgb1']['hsv'][2] }}"><br>-->
        <div id="color"></div>
        <hr>
        <label for="brightness">Simple led brightness</label><br>
        <input id="brightness" name="brightness" type="range" min="0" max="4095" step="5">
        <hr>
        <button name="rgb1off" id="rgb1off">RGB off</button>
        <button name="led1off" id="led1off">LED off</button>
        <hr>
        <b>Thermostat</b><br>
        Current temperature:
        <span class="temp-current">{{ ctx['thermostat']['val'] if ctx['thermostat']['val'] else "Unknown" }}</span>
        ({{ ctx['thermostat']['time'] if ctx['thermostat']['time'] else "" }})<br>
        Target temperature:
        <input type="number" min="50" max="85" step="1" name="temperature" id="temperature" value="{{ ctx['thermostat']['target'] }}">
        <div id="thermostat-control">
            <div id="up"></div>
            <div id="down"></div>
        </div>
    </form>

    <script src="/static/jquery-2.0.3.min.js"></script>
    <script src="/static/sldr.dist.js"></script>
    <script src="/static/jquery-minicolors/jquery.minicolors.js"></script>

    <script type="text/javascript">
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

            var curhex = "#" + componentToHex(parseInt({{ ctx['rgb1']['val'][0] }})) +
                               componentToHex(parseInt({{ ctx['rgb1']['val'][1] }})) +
                               componentToHex(parseInt({{ ctx['rgb1']['val'][2] }}));

            var col = $('#color').minicolors({
                inline: true,
                defaultValue: curhex,
                control: "saturation",
                change: function(hex, opacity) {
                    var result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);
                    ws.send(JSON.stringify({
                        target: "rgb1",
                        action: "set",
                        format: "rgb",
                        value: [
                            parseInt(result[1], 16) / 255,
                            parseInt(result[2], 16) / 255,
                            parseInt(result[3], 16) / 255
                        ]
                    }));
                }
            });

            $('#temperature').change(function(e) {
                ws.send(JSON.stringify({
                    target: "thermostat",
                    action: "set",
                    value: e.target.value
                }));
            });
            $('#rgb1off').click(function(e) {
                e.preventDefault()
                ws.send(JSON.stringify({
                    target: "rgb1",
                    action: "off"
                }));
                var curhex = "#" + componentToHex(parseInt({{ ctx['rgb1']['val'][0] }})) +
                                   componentToHex(parseInt({{ ctx['rgb1']['val'][1] }})) +
                                   componentToHex(parseInt({{ ctx['rgb1']['val'][2] }}));
                $('#color').minicolors('value', curhex);
            });
            $('#led1off').click(function(e) {
                e.preventDefault();
                ws.send(JSON.stringify({
                    target: "led1",
                    action: "off"
                }));
                $('#brightness').val(0);
            });
            function componentToHex(c) {
                var hex = c.toString(16);
                return hex.length == 1 ? "0" + hex : hex;
            }
        });
    </script>
</body>
</html>
