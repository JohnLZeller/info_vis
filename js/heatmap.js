var width = 960,
    height = 600;

var swag = d3.map();
var districtRatings1 = d3.map();
var districtRatings2 = d3.map();
var datasets = [d3.map(), d3.map(), d3.map()];

var us_map;
var us;
var congress;
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


queue()
    .defer(d3.tsv, "data/districts.tsv", function(d) { 
      //datasets[0].set(d.id, +d.district); 
      swag.set(d.district, d);
    })
    .defer(d3.json, "json/us_districts.json")
    .defer(d3.json, "json/us-congress-10m.json")
    .defer(d3.json, "json/us-10m.json")
    
    //.defer(d3.json, "json/usa_map.json")
    .awaitAll(loadingCallback);


function loadingCallback(error, map) {
  us_map = map[1];
  congress = map[2];
  us = map[3];
  drawMap(swag, us_map);
}


function drawMap(dataset, map) {
  svg.append("defs").append("path")
        .attr("id", "land")
        .datum(topojson.object(us, us.objects.land))
        .attr("d", path);

    svg.append("clipPath")
        .attr("id", "clip-land")
      .append("use")
        .attr("xlink:href", "#land");

    svg.append("g")
        .attr("class", "districts")
        .attr("clip-path", "url(#clip-land)")
      .selectAll("path")
        .data(topojson.object(congress, congress.objects.districts).geometries)
      .enter().append("path")
        .attr("class", function(d) { 
          if(dataset.has(d.id)) { 
            console.log(dataset.get(d.id));
            return quantize(dataset.get(d.id).amtRatio * 30); 
          }
        })
        .attr("d", path)
      .append("title")
        .text(function(d) { return d.id; });

    svg.append("path")
        .attr("class", "district-boundaries")
        .attr("clip-path", "url(#clip-land)")
        .datum(topojson.mesh(congress, congress.objects.districts, function(a, b) { return (a.id / 1000 | 0) === (b.id / 1000 | 0); }))
        .attr("d", path);

    svg.append("path")
        .attr("class", "state-boundaries")
        .datum(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; }))
        .attr("d", path);
}


d3.select('button').on('click', function() {
  datasetNumber += 1;
    currentDataset = swag;
    drawMap(currentDataset, us_map);
});


d3.select(self.frameElement).style("height", height + "px");
