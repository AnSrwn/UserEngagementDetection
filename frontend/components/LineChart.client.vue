<!-- Composition API -->
<script setup>
import {scaleLinear, scaleUtc} from "d3-scale";
import {line, curveMonotoneX} from "d3-shape";
import {axisBottom, axisLeft} from "d3-axis";
import {timeFormat} from "d3-time-format";
import {select} from "d3-selection";
import {extent} from "d3-array";
import { v4 as uuidv4 } from "uuid";

const margin = {top: 10, right: 30, bottom: 30, left: 50};
const width = 500 - margin.left - margin.right;
const height = 250 - margin.top - margin.bottom;

let svg = null;
let x = null;
let y = null;
let xAxis = null;
let yAxis = null;

const chartUuid = uuidv4();

const props = defineProps({
  data: Array,
});

function onChartDivMounted() {
  // append the svg object to the body of the page
  svg = select(`#line-chart-${chartUuid}`)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Initialise an X axis:
  const format = timeFormat("%H:%M");
  x = scaleUtc().range([0, width]);
  xAxis = axisBottom().scale(x).tickFormat(format).ticks(4);
  svg
      .append("g")
      .attr("transform", "translate(0," + height + ")")
      .attr("class", `xAxis-${chartUuid}`);

  // Initialize an Y axis
  y = scaleLinear().range([height, 0]);
  yAxis = axisLeft().scale(y).ticks(4);
  svg.append("g").attr("class", `yAxis-${chartUuid}`);

  updateChart(props.data);
  watch(
      () => props.data,
      (newValue, oldValue) => {
        if (newValue.length !== oldValue.length) {
          updateChart(newValue)
        }
      }
  );
}

function updateChart(data) {
  // Create the X axis:
  x.domain(extent(data, (d) => d.time));
  svg.selectAll(`.xAxis-${chartUuid}`).transition().duration(500).call(xAxis);

  // create the Y axis
  y.domain([0, 100]);
  svg.selectAll(`.yAxis-${chartUuid}`).transition().duration(500).call(yAxis);

  // Create an update selection: bind to the new data
  const u = svg.selectAll(`.line-${chartUuid}`).data([data], (d) => d.time);

  // Update the line
  u.enter()
      .append("path")
      .attr("class", `line-${chartUuid}`)
      .merge(u)
      // .transition()
      // .ease(easeSin)
      // .duration(1000)
      .attr(
          "d",
          line()
              // .defined((d) => d.time !== null)
              .x((d) => x(d.time))
              .y((d) => y(d.percentage))
              .curve(curveMonotoneX)
      )
      .attr("fill", "none") // black
      .attr("stroke", "black")
      .attr("stroke-width", 2.5);
}
</script>

<template>
  <div>
    <div
        v-bind:id="'line-chart-' + chartUuid"
        @vue:mounted="onChartDivMounted"
    ></div>
  </div>
</template>

<style lang='scss'></style>