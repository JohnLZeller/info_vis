var width = 960,
    height = 600;

var districtData = d3.map();

var us;
var congress;
var datasetNumber = 0;
var colorAttributes = ["amtRatio", "contRatio", "fundingDurationRatio"];

var quantize = d3.scale.quantize()
    .domain([0, .15])
    .range(d3.range(9).map(function(i) { return "q" + i + "-9"; }));

var projection = d3.geo.albersUsa()
    .scale(1280)
    .translate([width / 2, height / 2]);

var path = d3.geo.path()
    .projection(projection);

var svg = d3.select("#heatmap").append("svg");
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
      districtData.set(d.district, d);
    })
    .defer(d3.json, "json/us-congress-10m.json")
    .defer(d3.json, "json/us-10m.json")
    .awaitAll(loadingCallback);


function loadingCallback(error, map) {
  congress = map[1];
  us = map[2];
  drawMap(colorAttributes[datasetNumber]);
}


function drawMap(attribute) {
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
          if(districtData.has(d.id)) { 
            //console.log(districtData.get(d.id));
            return quantize(districtData.get(d.id)[attribute] * 5); 
          }
        })
        .attr("d", path)
      .append("title")
        .text(function(d) { 
          if(districtData.has(d.id)) { 
            return "Contracts: \t" + districtData.get(d.id).contracts +
              "\nValue:\t\t" + numeral(districtData.get(d.id).amt).format('$0a') + 
              "\nDuration: \t\t" + districtData.get(d.id).fundingDuration + " days"; 
          } else {
           return "No data"; 
          }
        });
            
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


d3.select('#heatmap_dataset').on('click', function() {
  datasetNumber = d3.select('input[name="heatmap_dataset"]:checked').node().value
  drawMap(colorAttributes[datasetNumber % 3]);
});


d3.select(self.frameElement).style("height", height + "px");
