<!-- Composition API -->
<script setup>
import { transition } from "d3-transition";
import { interpolate } from "d3-interpolate";
import { arc, pie } from "d3-shape";
import { scaleOrdinal } from "d3-scale";
import { select } from "d3-selection";
import { ref } from "vue";
import { v4 as uuidv4 } from "uuid";

const margin = 0;
const width = 450;
const height = 450;

const radius = Math.min(width, height) / 2 - margin;
const innerRadius = 140;
const cornerRadius = 8;
const padAngle = 0.01; // marign betwenn segments
const transitionDuration = 2000;
const color = scaleOrdinal().range(["#0aa849", "#e3df0b", "#a11f0b"]);

const chartUuid = uuidv4();

const props = defineProps({
  data: Object,
});

let svg = null;
let gElement = null;
let chartPie = null;
let chartArc = null;
let tooltip = null;
let chartData = ref({});

function onNewValue(newValue) {
  if (newValue === null) newValue = {};

  chartData.value = newValue;
  updateChart(Object.entries(newValue));
}

function onChartDivMounted() {
  // Setup donut chart
  svg = select(`#donut_chart-${chartUuid}`)
    .append("svg")
    .attr("viewBox", `0 0 ${width} ${height}`);

  gElement = svg
    .append("g")
    .attr("transform", `translate(${width / 2},${height / 2})`);

  // chartPie = pie()
  //   .startAngle(-(Math.PI / 2) * 5)
  //   .value((d) => d[1])
  //   .sort(null)
  //   .padAngle(padAngle);

  chartArc = arc()
    .innerRadius(innerRadius)
    .outerRadius(radius)
    .cornerRadius(cornerRadius);

  tooltip = select(`#donut_chart-${chartUuid}`)
    .append("div")
    .attr("id", "tooltip")
    .attr("class", "toolTip").html(`
      <div class="tooltip-value">
        <span id="value"></span> User
      </div>
    `);

  // Handle new data
  onNewValue(props.data);
  watch(
    () => props.data,
    (newValue, oldValue) => {
      onNewValue(newValue);
    }
  );
}

function onMouseEnter(d) {
  const x = chartArc.centroid(d) + width / 2;
  const y = chartArc.centroid(d) + height / 2;

  // console.log(select(this));
  console.log(d);
  console.log(d.data);
  console.log(d.data());

  tooltip.style("opacity", 1);
  tooltip.style(
    "transform",
    `translate(calc( -50% + ${x}px), calc(-100% + ${y}px))`
  );
  tooltip.select("#value").text(d.explicitOriginalTarget.__data__.value);
}

function onMouseLeave(d) {
  tooltip.style("opacity", 0);
}

// Store the displayed angles in _current.
// Then, interpolate from _current to the new angles.
// During the transition, _current is updated in-place by d3.interpolate.
function arcTween(a) {
  var i = interpolate(this._current, a);
  this._current = i(0);
  return function (t) {
    return chartArc(i(t));
  };
}

function updateChart(data) {
  chartPie = pie()
    .startAngle(-(Math.PI / 2) * 5)
    .value((d) => d[1])
    .sort(null)
    .padAngle(padAngle)(data, (d) => d[0]);

  // add transition to new path
  gElement
    .selectAll("path")
    .transition()
    .duration(transitionDuration)
    .attrTween("d", arcTween);

  // add new data
  gElement
    .selectAll("path")
    .data(chartPie, function (d) {
      return d.data[0];
    })
    .enter() // There was no matching element for a given datum.
    .append("path")
    .attr("class", `donut_chart-${chartUuid}`)
    .attr("fill", (d) => color(d.data[0]))
    .attr("d", chartArc)
    .each(function (d) {
      this._current = d;
    });

  // add tooltips
  gElement.on("mouseenter", onMouseEnter).on("mouseleave", onMouseLeave);

  // remove data not used
  gElement.exit().remove();
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

<style lang='scss'>
</style>