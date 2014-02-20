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
    <div class="navbar navbar-default">
        <div class="container-fluid">
            <div class="navbar-header">
                <p class="navbar-brand" href="#">Homedo
                </p>
            </div>
        </div>
    </div>

    <div class="container">
        <div class="row">
            <div class="col-lg-6 col-lg-offset-3 col-md-8 col-md-offset-2">
                <h3>Login</h3>
                <form action="login" method="post" name="login" role="form">
                    <div class="form-group">
                        <input class="form-control" type="text" name="username" placeholder="username">
                    </div>
                    <div class="form-group">
                        <input class="form-control" type="password" name="password" placeholder="password">
                    </div>

                    <button type="submit" class="btn btn-primary">Log in</button>
                </form>
            </div>
        </div>
    </div>
    <script src="/static/js/libs/jquery-2.1.0.min.js"></script>
    <script src="/static/libs/bootstrap/js/bootstrap.min.js"></script>
</body>
</html>
