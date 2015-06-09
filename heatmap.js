var width = 960,
    height = 600;

var districtRatings1 = d3.map();
var districtRatings2 = d3.map();
var datasets = [d3.map(), d3.map(), d3.map()];

var us_map;
var datasetNumber = 1;
var currentDataset = districtRatings1;

var quantize = d3.scale.quantize()
    .domain([0, .15])
    .range(d3.range(9).map(function(i) { return "q" + i + "-9"; }));

var projection = d3.geo.albersUsa()
    .scale(1280)
    .translate([width / 2, height / 2]);

var path = d3.geo.path()
    .projection(projection);

var svg = d3.select("body").append("svg")
    .attr("width", width)
    .attr("height", height);

var tip = d3.tip()
  .attr('class', 'd3-tip')
  .offset([-10, 0])
  .html(function(d) {
    //console.log(JSON.stringify(d));
    return "<strong>Rating:</strong> <span style='color:red'>" + d.id + "</span>";
  });

svg.call(tip);



dataset1 = d3.tsv("unemployment.tsv", function(error, data) {
//  x.domain(data.map(function(d) { return d.x; }));
//  y.domain([0, d3.max(data, function(d) { return d.y; })]);
});


queue()
    .defer(d3.json, "usa_map.json", function(d) { us_map = d; })
    .defer(d3.tsv, "unemployment.tsv", function(d) { districtRatings1.set(d.id, +d.rate); })
    .defer(d3.tsv, "contracts-amounts.tsv", function(d) { datasets[0].set(d.id, +d.cont-ratio); datasets[1].set(d.id, +d.amt-ratio); })
    .awaitAll(function(a, b) { drawMap(us_map, currentDataset); });

function drawMap(datasetNumber) {
    svg.append("g")
        .attr("class", "counties")
      .selectAll("path")
        .data(topojson.feature(map, map.objects.counties).features)
      .enter().append("path")
        .attr("class", function(d) { return quantize(dataset.get(d.id)); })
        .attr("d", path)
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);

    svg.append("path")
        .datum(topojson.mesh(map, map.objects.states, function(a, b) { return a !== b; }))
        .attr("class", "states")
        .attr("d", path);
}

//function yolo(error, a, b, c) {
//  drawMap(us_map, districtRatings1);
//}

setTimeout(function() { drawMap(us_map, districtRatings1); }, 2000);

d3.select('button').on('click', function() {
    if ( datasetNumber == 1 ) {
      datasetNumber = 2;
    } else {
      datasetNumber = 1;
    }
    currentDataset = datasets[datasetNumber];
    drawMap(us_map, currentDataset);
});


d3.select(self.frameElement).style("height", height + "px");
