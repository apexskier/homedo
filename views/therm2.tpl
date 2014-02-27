<!doctype html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <title></title>
    <link rel="stylesheet" href="/static/libs/bootstrap/css/bootstrap.min.css">
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <div class="navbar navbar-default navbar-fixed-top">
        <div class="container-fluid">
            <div class="navbar-header">
                <p class="navbar-brand" href="#">Homedo&nbsp;&nbsp;
                    <small><a href="/">{{ ctx['therm']['name']}}</a>&nbsp;&nbsp;
                    <a href="/rgb">{{ ctx['rgb1']['name']}}</a>&nbsp;&nbsp;
                    <a href="/logout">Logout</a></small>
                </p>
            </div>
        </div>
    </div>
    <div class="container-fluid content">
        <div class="content-inner" id="main">
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

    <script src="/static/libs/color-conversion-algorithms.js"></script>
    <script src="/static/libs/draggabilly.pkgd.min.js"></script>
    <script src="http://d3js.org/d3.v3.min.js" charset="utf-8"></script>
    <script>
        var targettemp = {{ ctx['therm']['target'] }};
        var bounds = {
            top: 85,
            bot: 50
        }
        var currenttemp = {{ ctx['therm']['val'] if ctx['therm']['val'] else "bounds.bot" }};
        var curperc = (currenttemp - bounds.bot) / (bounds.top - bounds.bot);
    </script>
    <script src="/static/js/therm2.js"></script>
</body>
</html>
