var width = 960,
    height = 600;

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

var us;
var attributeNumber = 0;
var datasets = [d3.map(), d3.map()];
var mapNumber = 0;
var maps = [];
var colorAttributes = ["amtRatio", "contRatio", "fundingDurationRatio"];
var mapOptions = ["districts", "states"];

var quantize = d3.scale.quantize()
    .domain([0, .15])
    .range(d3.range(9).map(function(i) { return "q" + i + "-9"; }));

var projection = d3.geo.albersUsa()
    .scale(1280)
    .translate([width / 2, height / 2]);

var path = d3.geo.path()
    .projection(projection);

var svg1 = d3.select("#heatmap").append("svg")
    .attr("width", width)
    .attr("height", height);

var tip = d3.tip()
  .attr('class', 'd3-tip')
  .offset([-10, 0])
  .html(function(d) {
    //console.log(JSON.stringify(d));
    return "<strong>Rating:</strong> <span style='color:red'>" + d.id + "</span>";
  });


svg1.call(tip);


queue()
    .defer(d3.tsv, "data/districts.tsv", function(d) { 
      datasets[0].set(d.district, d);
    })
    .defer(d3.json, "json/us-congress-10m.json")
    .defer(d3.json, "json/us-10m.json")
    .defer(d3.json, "json/us-states-10m.json")
    .defer(d3.tsv, "data/states.tsv", function(d) { 
      datasets[1].set(d.state, d);
    })
    .awaitAll(loadingCallback);


function loadingCallback(error, map) {
  maps[0] = map[1];
  us = map[2];
  maps[1] = map[3];
  drawMap(colorAttributes[attributeNumber]);
}


function drawMap(attribute) {
  svg1.append("defs").append("path")
        .attr("id", "land")
        .datum(topojson.object(us, us.objects.land))
        .attr("d", path);

  svg1.append("clipPath")
      .attr("id", "clip-land")
    .append("use")
      .attr("xlink:href", "#land");

  svg1.append("g")
      .attr("class", "districts")
      .attr("clip-path", "url(#clip-land)")
    .selectAll("path")
      .data(topojson.object(maps[mapNumber],
            maps[mapNumber].objects[mapOptions[mapNumber]]).geometries)
    .enter().append("path")
      .attr("class", function(d) { 
        if(datasets[mapNumber].has(d.id)) { 
          return quantize(datasets[mapNumber].get(d.id)[attribute]); 
        }
      })
      .attr("d", path)
    .append("title")
      .text(function(d) { 
        if(datasets[mapNumber].has(d.id)) { 
          return "Contracts: \t" + numberWithCommas(datasets[mapNumber].get(d.id).contracts) +
            "\nValue: \t\t$" + numberWithCommas(datasets[mapNumber].get(d.id).amt) + 
            "\nDuration: \t\t" + numberWithCommas(datasets[mapNumber].get(d.id).fundingDuration) + 
            " day(s)"; 
        } else {
         return "No contracts"; 
        }
      });
          
  svg1.append("path")
      .attr("class", "district-boundaries")
      .attr("clip-path", "url(#clip-land)")
      .datum(topojson.mesh(maps[mapNumber], maps[mapNumber].objects[mapOptions[mapNumber]], function(a, b) { return (a.id / 1000 | 0) === (b.id / 1000 | 0); }))
      .attr("d", path);

  svg1.append("path")
      .attr("class", "state-boundaries")
      .datum(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; }))
      .attr("d", path);
}


var datasetForm = d3.select('#heatmap_dataset')
datasetForm[0][0].reset();
datasetForm.on('click', function() {
  attributeNumber = d3.select('input[name="heatmap_dataset"]:checked').node().value
  drawMap(colorAttributes[attributeNumber]);
});


var bordersForm = d3.select('#heatmap_borders')
bordersForm[0][0].reset();
bordersForm.on('click', function() {
  mapNumber = d3.select('input[name="heatmap_borders"]:checked').node().value
  drawMap(colorAttributes[attributeNumber]);
});


d3.select(self.frameElement).style("height", height + "px");
