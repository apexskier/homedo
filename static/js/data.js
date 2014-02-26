var m = [30, 30, 30, 30], // margins
    h = window.innerHeight - 120 - m[0] - m[2],
    w = window.innerWidth - 30 - m[1] - m[3];

var time_x = d3.time.scale().range([0, w]),
    val_y = d3.scale.linear().range([h, 0]);

var timeAxisX = d3.svg.axis().scale(time_x).orient('bottom'),
    valAxisY = d3.svg.axis().scale(val_y).orient('left');

var area = d3.svg.area()
    .interpolate('monotone')
    .x(function(d) { return time_x(d.time); })
    .y0(h)
    .y1(function(d) { return val_y(d.val); });

var svg = d3.select('#main').append('svg')
    .attr('width', w + m[1] + m[3])
    .attr('height', h + m[0] + m[2]);

var days = {
    'Mon': 0,
    'Tue': 1,
    'Wed': 2,
    'Thu': 3,
    'Fri': 4,
    'Sat': 5,
    'Sun': 6
}

d3.json(jsonfile, function(err, json) {
    if (err) return console.warn(err);
    var lm = getMonday(new Date());
    var now = new Date();
    function getMonday(d) {
        d = new Date(d);
        var day = d.getDay(),
            diff = d.getDate() - day + (day == 0 ? -6:1); // adjust when day is sunday
        var nd = new Date(d.setDate(diff));
        nd.setHours(0, 0, 0, 0);
        return nd;
    }
    console.log(lm);
    json.forEach(function(el) {
        var day = days[el.time.split(' ')[0]];
        var time = el.time.split(' ')[1].split(':');
        var d = new Date(lm);
        d.setDate(lm.getDate() + day);
        d.setHours(time[0], time[1], time[2]);
        el.time = d;
    });
    json.sort(function(a, b) {
        return a.time - b.time;
    });
    var data = [];
    var certainraw = json.filter(function(el) {
        return el.certain;
    });
    json.forEach(function(el, i) {
        data.push(el);
        if (i + 1 < json.length) {
            var n = {
                time: new Date(json[i + 1].time - 1),
                val: el.val,
            };
            data.push(n);
        }
    });
    var certain = []
    certainraw.forEach(function(el, i) {
        certain.push(el);
        if (i + 1 < certainraw.length) {
            var n = {
                time: new Date(certainraw[i + 1].time - 1),
                val: el.val,
            };
            certain.push(n);
        }
    });

    time_x.domain(d3.extent(data.map(function(d) { return d.time; })));
    val_y.domain([0, d3.max(data.map(function(d) { return d.val; }))]);

    var graph = svg.append('g').attr('transform', 'translate(' + m[3] + ',' + m[0] + ')')
    graph.append('g').attr('class', 'x axis').attr('transform', "translate(0," + h + ")").call(timeAxisX);
    graph.append('g').attr('class', 'y axis').call(valAxisY);

    var line = d3.svg.line()
        .x(function(d, i) {
            return time_x(d.time);
        })
        .y(function(d, i) {
            return val_y(d.val);
        });

    var r = jsonfile.split('/')
    d3.json('/data/real-' + r[r.length - 1], function(err, json) {
        if (err) return console.warn(err);
        json.forEach(function(el) {
            el.time = new Date(el.time);
        });
        data = json.filter(function(el) {
            return el.time > lm;
        });
        console.log(data);
        graph.append('path').attr('d', line(data)).attr('class', 'line real');
    })

    var valpoint = graph.append('circle')
        .attr('cx', function(d) { return time_x(now); })
        .attr('cy', function(d) { return val_y(curval); })
        .attr('r', 3.5)
        .attr('class', 'val');
    var targetpoint = graph.append('circle')
        .attr('cx', function(d) { return time_x(now); })
        .attr('cy', function(d) { return val_y(curtar); })
        .attr('r', 3.5)
        .attr('class', 'target');

    graph.append('path').attr('d', line(certain)).attr('class', 'line certain');
    graph.append('path').attr('d', line(data)).attr('class', 'line uncertain');
});
