<!-- Composition API -->
<script setup>
import {scaleLinear, scaleUtc} from "d3-scale";
import {transition} from "d3-transition";
import {line} from "d3-shape";
import {axisBottom, axisLeft} from "d3-axis";
import {timeFormat} from "d3-time-format";
import {select} from "d3-selection";
import {extent} from "d3-array";
import {ref} from "vue";

const margin = {top: 10, right: 30, bottom: 30, left: 50};
const width = 460 - margin.left - margin.right;
const height = 250 - margin.top - margin.bottom;

let svg = null;
let x = null;
let y = null;
let xAxis = null;
let yAxis = null;

let chartData = ref([]);

const props = defineProps({
  data: Array,
});

function onNewValue(newValue) {
  if (newValue === null) newValue = Array();

  // chartData.value = chartData.value.concat(newValue);

  // console.log(chartData.value)

  console.log(newValue)
  // let test = toDeepRaw(newValue)
  // chartData.value = chartData.value.concat(newValue);
  chartData.value = newValue
  // console.log(chartData.value)

  // chartData.value.push({ from_datetime: "2023-08-06T09:02:00.113867", avg_engagement: 32.49})
  // chartData.value.push({ from_datetime: "2023-08-06T09:02:05.113867", avg_engagement: 62.49})
  // chartData.value.push({ from_datetime: "2023-08-06T09:02:10.113867", avg_engagement: 12.49})
  // console.log(chartData.value)

  updateChart(chartData.value)
}

function onChartDivMounted() {
  // append the svg object to the body of the page
  svg = select(`#line-chart`)
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // Initialise an X axis:
  const format = timeFormat("%X");
  x = scaleUtc().range([0, width]);
  xAxis = axisBottom().scale(x).tickFormat(format);
  svg
      .append("g")
      .attr("transform", "translate(0," + height + ")")
      .attr("class", `xAxis`);

  // Initialize an Y axis
  y = scaleLinear().range([height, 0]);
  yAxis = axisLeft().scale(y);
  svg.append("g").attr("class", `yAxis`);

  onNewValue(props.data)
  watch(
      () => props.data,
      (newValue, oldValue) => {
        onNewValue(newValue);
      }
  );
}

function updateChart(data) {
  // Create the X axis:
  x.domain(extent(data, (d) => d.from_datetime));
  svg.selectAll(`.xAxis`).transition().duration(500).call(xAxis);

  // create the Y axis
  y.domain([0, 100]);
  svg.selectAll(`.yAxis`).transition().duration(500).call(yAxis);

  // svg.append("path")
  //     .datum(data).attr("fill", "none")
  //     .attr("stroke", "steelblue")
  //     .attr("stroke-width", 1.5)
  //     .attr("d", line()
  //         .x(function (d) {
  //           return x(d.from_datetime)
  //         })
  //         .y(function (d) {
  //           return y(d.avg_engagement)
  //         })
  //     )

  // Create an update selection: bind to the new data
  const u = svg.selectAll(`.line`).data([data], (d) => d.from_datetime);

  // Update the line
  u.enter()
      .append("path")
      .attr("class", `line`)
      .merge(u)
      .transition()
      .duration(1000)
      .attr(
          "d",
          line()
              .x((d) => x(d.from_datetime))
              .y((d) => y(d.avg_engagement))
      )
      .attr("fill", "none")
      .attr("stroke", "steelblue")
      .attr("stroke-width", 1.5);
}
</script>

<template>
  <div>
    <div
        v-bind:id="'line-chart'"
        @vue:mounted="onChartDivMounted"
    ></div>
  </div>
</template>

<style lang='scss'></style>