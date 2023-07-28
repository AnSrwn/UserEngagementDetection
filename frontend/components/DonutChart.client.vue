<!-- Composition API -->
<script setup>
import { transition } from "d3-transition";
import { line, arc, pie } from "d3-shape";
import { scaleLinear, scaleUtc, scaleOrdinal } from "d3-scale";
import { axisBottom, axisLeft } from "d3-axis";
import { timeFormat } from "d3-time-format";
import { select } from "d3-selection";
import { extent, max } from "d3-array";
import { ref } from "vue";
import { v4 as uuidv4 } from "uuid";

// Declare the chart dimensions and margins.
// set the dimensions and margins of the graph
const margin = 40;
const width = 450;
const height = 450;

const radius = Math.min(width, height) / 2 - margin;
const color = scaleOrdinal().range(["#0aa849", "#e3df0b", "#a11f0b"]);

let svg = null;
let chartData = ref({});

const props = defineProps({
  data: Object,
});

const chartUuid = uuidv4();

function onNewValue(newValue) {
  if (newValue === null) newValue = {};

  chartData.value = newValue;
  updateChart(newValue);
}

function onChartDivMounted() {
  // append the svg object to the body of the page
  svg = select(`#donut_chart-${chartUuid}`)
    .append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
    .attr("transform", `translate(${width / 2},${height / 2})`);

  onNewValue(props.data);
  watch(
    () => props.data,
    (newValue, oldValue) => {
      onNewValue(newValue);
    }
  );
}

function updateChart(data) {
  // Compute the position of each group on the pie:
  var pieChart = pie()
    .startAngle(-(Math.PI / 2) * 5)
    .value((d) => d[1])
    .sort(null)(Object.entries(data));

  // const data_ready = pieChart(Object.entries(data));

  // Create a update selection: bind to the new data
  var u = svg.selectAll(`.donut_chart-${chartUuid}`).data(pieChart);

  // Updata the line
  u.enter()
    .append("path")
    .attr("class", `donut_chart-${chartUuid}`)
    .merge(u)
    .transition()
    .duration(2000)
    .attr(
      "d",
      arc()
        .innerRadius(100) // This is the size of the donut hole
        .outerRadius(radius)
    )
    .attr("fill", (d) => color(d.data[0]))
    .attr("stroke", "black")
    .style("stroke-width", "2px");

  // Build the pie chart: Basically, each part of the pie is a path that we build using the arc function.
  // svg
  //   .selectAll(`#donut_chart-${chartUuid}`)
  //   .data(data_ready)
  //   .join("path")
  //   .attr(
  //     "d",
  //     arc()
  //       .innerRadius(100) // This is the size of the donut hole
  //       .outerRadius(radius)
  //   )
  //   .attr("fill", (d) => color(d.data[0]))
  //   .attr("stroke", "black")
  //   .style("stroke-width", "2px");
}
</script>

<template>
  <div>
    <div
      @vue:mounted="onChartDivMounted"
      v-bind:id="'donut_chart-' + chartUuid"
    ></div>
  </div>
</template>

<style lang='scss'></style>