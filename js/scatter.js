var margin = {top: 20, right: 20, bottom: 30, left: 40},
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom,
    xOffset = 50;

function numberWithCommas(x) {
    return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

/* 
 * value accessor - returns the value to encode for a given data object.
 * scale - maps value to a visual display encoding, such as a pixel position.
 * map function - maps from data value to display value
 * axis - sets up axis
 */ 

// setup x 
var xValue = function(d) { return d.employees;}, // data -> value
    xScale = d3.scale.linear().range([xOffset, width + xOffset]), // value -> display
    xMap = function(d) { return xScale(xValue(d));}, // data -> display
    xAxis = d3.svg.axis().scale(xScale).orient("bottom");

// setup y
var yValue = function(d) { return d.amt;}, // data -> value
    yScale = d3.scale.linear().range([height, 0]), // value -> display
    yMap = function(d) { return yScale(yValue(d));}, // data -> display
    yAxis = d3.svg.axis().scale(yScale).orient("left");

// add the graph canvas to the body of the webpage
var svg2 = d3.select("#scatter").append("svg")
    .attr("width", width + margin.left + margin.right + xOffset)
    .attr("height", height + margin.top + margin.bottom)
    .style("margin-left", "-" + xOffset + "px")
  .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

var tip = d3.tip()
  .attr('class', 'd3-tip')
  .offset([-10, 0])
  .html(function(d) {
    //console.log(JSON.stringify(d));
    return "<strong>Rating:</strong> <span style='color:red'>" + d.id + "</span>";
  });

svg2.call(tip);

// load data
d3.tsv("data/companies.tsv", function(error, data) {

  // change string (from CSV) into number format
  data.forEach(function(d) {
    d.employees = +d.employees;
    d.amt = +d.amt;
//    console.log(d);
  });

  // don't want dots overlapping axis, so add in buffer to data domain
  xScale.domain([d3.min(data, xValue)-1, d3.max(data, xValue)+1]);
  yScale.domain([d3.min(data, yValue)-1, d3.max(data, yValue)+1]);

  // x-axis
  svg2.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
    .append("text")
      .attr("class", "label")
      .attr("x", width + xOffset)
      .attr("y", -6)
      .style("text-anchor", "end")
      .text("Employees");

  // y-axis
  svg2.append("g")
      .attr("class", "y axis")
      .attr("transform", "translate(" + xOffset + ", 0)")
      .call(yAxis)
    .append("text")
      .attr("class", "label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text("Total Contracts Value ($)");

  // draw dots
  svg2.selectAll(".dot")
      .data(data)
    .enter().append("circle")
      .attr("class", "dot")
      .attr("r", 3.5)
      .attr("cx", xMap)
      .attr("cy", yMap)
      .style("fill", "#02326B")
    .append("title")
      .text(function(d) { 
        return d.company + "\n\nContracts: \t" + numberWithCommas(d.contracts) +
          "\nValue: \t\t$" + numberWithCommas(yValue(d)) + 
          "\nEmployees: \t" + numberWithCommas(xValue(d));
      });

});
