<!-- Composition API -->
<script setup>
import { transition } from "d3-transition";
import { line } from "d3-shape";
import { scaleLinear, scaleUtc } from "d3-scale";
import { axisBottom, axisLeft } from "d3-axis";
import { timeFormat } from "d3-time-format";
import { select } from "d3-selection";
import { extent, max } from "d3-array";
import { ref } from "vue";

// Declare the chart dimensions and margins.
// set the dimensions and margins of the graph
const margin = { top: 10, right: 30, bottom: 30, left: 50 };
const width = 460 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

let svg = null;
let x = null;
let y = null;
let xAxis = null;
let yAxis = null;

const chartDiv = ref(null);
let chartData = ref([]);

const props = defineProps({
  data: Array,
});

onMounted(() => {
  watch(
    () => props.data,
    (newValue, oldValue) => {
      if (newValue === null) newValue = Array()
      
      chartData.value = newValue;

      if (newValue.length) {
        updateChart(newValue);
      }
    }
  );
});

function onchartDivMounted() {
  // append the svg object to the body of the page
  svg = select("#myplot")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Initialise a X axis:
  var format = timeFormat("%X");
  x = scaleUtc().range([0, width]);
  xAxis = axisBottom().scale(x).tickFormat(format);
  svg
    .append("g")
    .attr("transform", "translate(0," + height + ")")
    .attr("class", "myXaxis");

  // Initialize an Y axis
  y = scaleLinear().range([height, 0]);
  yAxis = axisLeft().scale(y);
  svg.append("g").attr("class", "myYaxis");
}

function updateChart(data) {
  // Create the X axis:
  x.domain(extent(data, (d) => d.time));
  svg.selectAll(".myXaxis").transition().duration(500).call(xAxis);

  // create the Y axis
  y.domain([0, max(data, (d) => d.engagement)]);
  svg.selectAll(".myYaxis").transition().duration(500).call(yAxis);

  // Create a update selection: bind to the new data
  var u = svg.selectAll(".line").data([data], function (d) {
    return d.time;
  });

  // Updata the line
  u.enter()
    .append("path")
    .attr("class", "line")
    .merge(u)
    .transition()
    .duration(1000)
    .attr(
      "d",
      line()
        .x(function (d) {
          return x(d.time);
        })
        .y(function (d) {
          return y(d.engagement);
        })
    )
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-width", 1.5);
}
</script>

<template>
  <div>
    <h2>Engagement:</h2>
    <div @vue:mounted="onchartDivMounted" ref="chartDiv" id="myplot"></div>
  </div>
</template>

<style lang='scss'></style>