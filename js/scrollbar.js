
var margin2 = {top: 20, right: 20, bottom: 30, left: 40},
    width2 = 960 - margin2.left - margin2.right,
    height2 = 600 - margin2.top - margin2.bottom,
    xOffset2 = 50;

var x = d3.scale.ordinal()
    .rangeRoundBands([0, width2], .1);

var y = d3.scale.linear()
    .range([height2, 0]);

var xAxis2 = d3.svg.axis()
    .scale(x)
    .orient("bottom");

var yValue2 = function(d) { return d.amt;}, // data -> value
    yScale2 = d3.scale.linear().range([height2, 0]), // value -> display
    yMap2 = function(d) { return yScale2(yValue2(d));}, // data -> display
    yAxis2 = d3.svg.axis().scale(yScale2).orient("left");

var svg3 = d3.select("#scrollbarchart").append("svg")
    .attr("width", width2 + margin2.left + margin2.right + xOffset2)
    .attr("height", height2 + margin2.top + margin2.bottom)
    .style("margin-left", "-" + xOffset2 + "px")
  .append("g")
    .attr("transform", "translate(" + margin2.left + "," + margin2.top + ")");

d3.tsv("data/data.tsv", type, function(error, data) {
  x.domain(data.map(function(d) { return d.company; }));
  y.domain([0, d3.max(data, function(d) { return d.amt; })]);

  svg3.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(" + xOffset2 + "," + height2 + ")")
      .call(xAxis2)
      .selectAll("text")
        .style("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em")
        .attr("transform", "rotate(-65)");

  svg3.append("g")
      .attr("class", "y axis")
      .attr("transform", "translate(" + xOffset2 + ", 0)")
      .call(yAxis2)
    .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Total Contracts Value ($)");

  svg3.selectAll(".bar")
      .data(data)
    .enter().append("rect")
      .attr("class", "bar")
      .attr("x", function(d) { return x(d.company) + xOffset2; })
      .attr("width", x.rangeBand())
      .attr("y", function(d) { return y(d.amt); })
      .attr("height", function(d) { return height2 - y(d.amt); });

});

function type(d) {
  d.amt = +d.amt;
  return d;
}
