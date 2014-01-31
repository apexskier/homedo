<!doctype html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title></title>

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
    </style>
</head>
<body>
    <form>
        <label for="hsl">HSL</label><br>
        <input id="hue" name="hue" type="range" min="0" max="1" step=".003921569"><br>
        <input id="sat" name="sat" type="range" min="0" max="1" step=".003921569" value="1"><br>
        <input id="light" name="light" type="range" min="0" max="1" step=".003921569"><br>
        <hr>
        <label for="brightness">Simple led brightness</label><br>
        <input id="brightness" name="brightness" type="range" min="0" max="4095" step="5">
        <hr>
        <button name="rgb1off" id="rgb1off">RGB off</button>
        <button name="led1off" id="led1off">LED off</button>
        <hr>
        <b>Thermostat</b><br>
        Current temperature: <span class="temp-current">{{ current_temp if current_temp else "Unknown" }}</span>{{ last_time if last_time else ""}}<br>
        Target temperature: <input type="number" min="50" max="85" step="1" name="temperature" id="temperature" value="{{ target_temp }}">
    </form>
    <script src="/static/jquery-2.0.3.min.js"></script>

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
            $('#brightness').change(function(e) {
                ws.send(JSON.stringify({
                    target: "led1",
                    action: "set",
                    value: e.target.valueAsNumber
                }));
            });
            $('#hue, #sat, #light').change(function() {
                var color = HSVtoRGB(parseFloat($('#hue').val()), parseFloat($('#sat').val()), parseFloat($('#light').val()));
                ws.send(JSON.stringify({
                    target: "rgb1",
                    action: "set",
                    value: rgbToHex(color.r, color.g, color.b)
                }));
            });
            $('#sat, #light').change(function(e) {
                $('#hue').css('background-image', '-webkit-linear-gradient(left,' +
                    'hsla(0,   100%, ' + (parseFloat($('#light').val()) * 50) + '%, ' + parseFloat($('#sat').val()) + ') 0%,' +
                    'hsla(120, 100%, ' + (parseFloat($('#light').val()) * 50) + '%, ' + parseFloat($('#sat').val()) + ') 33.3333%,' +
                    'hsla(240, 100%, ' + (parseFloat($('#light').val()) * 50) + '%, ' + parseFloat($('#sat').val()) + ') 66.6667%,' +
                    'hsla(360, 100%, ' + (parseFloat($('#light').val()) * 50) + '%, ' + parseFloat($('#sat').val()) + ') 100%)');
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
                $('#light').val(0);
                $('#hue').css('background-image', '-webkit-linear-gradient(left,' +
                    'hsla(0,   100%, 0%, ' + parseFloat($('#sat').val()) + ') 0%,' +
                    'hsla(120, 100%, 0%, ' + parseFloat($('#sat').val()) + ') 33.3333%,' +
                    'hsla(240, 100%, 0%, ' + parseFloat($('#sat').val()) + ') 66.6667%,' +
                    'hsla(360, 100%, 0%, ' + parseFloat($('#sat').val()) + ') 100%)');
            });
            $('#led1off').click(function(e) {
                e.preventDefault();
                ws.send(JSON.stringify({
                    target: "led1",
                    action: "off"
                }));
                $('#brightness').val(0);
            });
        });
        function HSVtoRGB(h, s, v) {
            var r, g, b, i, f, p, q, t;
            if (h && s === undefined && v === undefined) {
                s = h.s, v = h.v, h = h.h;
            }
            i = Math.floor(h * 6);
            f = h * 6 - i;
            p = v * (1 - s);
            q = v * (1 - f * s);
            t = v * (1 - (1 - f) * s);
            switch (i % 6) {
                case 0: r = v, g = t, b = p; break;
                case 1: r = q, g = v, b = p; break;
                case 2: r = p, g = v, b = t; break;
                case 3: r = p, g = q, b = v; break;
                case 4: r = t, g = p, b = v; break;
                case 5: r = v, g = p, b = q; break;
            }
            return {
                r: Math.floor(r * 255),
                g: Math.floor(g * 255),
                b: Math.floor(b * 255)
            };
        }
        function componentToHex(c) {
            var hex = c.toString(16);
            return hex.length == 1 ? "0" + hex : hex;
        }
        function rgbToHex(r, g, b) {
            return "#" + componentToHex(r) + componentToHex(g) + componentToHex(b);
        }
    </script>
</body>
</html>
