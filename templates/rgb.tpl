<!doctype html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, user-scalable=no">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title></title>
    <meta name="viewport" content="user-scalable=yes, initial-scale=1.0, maximum-scale=2.0, width=device-width">
    <link rel="stylesheet" href="/static/libs/bootstrap/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="navbar navbar-default navbar-fixed-top">
        <div class="container-fluid">
            <div class="navbar-header">
                <p class="navbar-brand" href="#">Homedo&nbsp;&nbsp;
                    <small><a href="/">{{ ctx['therm']['name']}}</a>&nbsp;&nbsp;
                    <a href="/rgb">{{ ctx['rgb1']['name']}}</a></small>
                </p>
            </div>
        </div>
    </div>
    <div class="container-fluid content">
        <div class="content-inner">
            <div class="col-xs-4 hue">
                <div class="inner">
                    <div class="handle"></div>
                </div>
            </div>
            <div class="col-xs-4 sat">
                <div class="inner">
                    <div class="handle"></div>
                </div>
            </div>
            <div class="col-xs-4 vib">
                <div class="inner">
                    <div class="handle"></div>
                </div>
            </div>
        </div>
    </div>
    <div class="navbar navbar-default navbar-fixed-bottom" id="bottom">
        <div class="container-fluid">
            <div class="row">
                <div class="col-xs-6">
                    <button id="off" class="btn btn-default navbar-btn btn-block">Off</button>
                </div>
                <div class="col-xs-6">

                </div>
            </div>
        </div>
        <div class="collapse navbar-collapse">
        </div>
    </div>
    <script src="/static/libs/color-conversion-algorithms.js"></script>
    <script src="/static/libs/jquery-2.1.0.min.js"></script>
    <script src="/static/libs/draggabilly.pkgd.min.js"></script>
    <script src="/static/libs/bootstrap/js/bootstrap.min.js"></script>
    <script src="/static/libs/jquery.stayInWebApp.min.js"></script>
    <script>
        $(document).ready(function() {
            $(function() {
                $.stayInWebApp('.navbar-header a');
            });
        });

        var rgb1 = {
            h: {{ ctx['rgb1']['hsv'][0] }},
            s: {{ ctx['rgb1']['hsv'][1] }},
            v: {{ ctx['rgb1']['hsv'][2] }},
        }
    </script>
    <script src="/static/js/rgb.js"></script>
</body>
</html>

