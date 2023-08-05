<!-- Composition API -->
<script setup>
import {transition} from "d3-transition";
import {interpolate} from "d3-interpolate";
import {arc, pie} from "d3-shape";
import {scaleOrdinal} from "d3-scale";
import {select} from "d3-selection";
import {ref} from "vue";

const margin = 0;
const width = 450;
const height = 450;

const radius = Math.min(width, height) / 2 - margin;
const innerRadius = 140;
const cornerRadius = 8;
const padAngle = 0.01; // marign betwenn segments
const transitionDuration = 2000;
const color = scaleOrdinal().range(["#0aa849", "#e3df0b", "#a11f0b"]);

const props = defineProps({
  data: Object,
});

let svg = null;
let gElement = null;
let chartPie = null;
let chartArc = null;
let chartData = ref({});

let highlyEngagedCount = ref(0);
let midlyEngagedCount = ref(0);
let lowlyEngagedCount = ref(0);
let highlyEngagedPercentage = ref(0);
let midlyEngagedPercentage = ref(0);
let lowlyEngagedPercentage = ref(0);

function getUserCount(engagementData) {
  return engagementData.high + engagementData.middle + engagementData.low;
}

function updateTooltip(engagementData) {
  let userCount = getUserCount(engagementData);
  highlyEngagedCount.value = engagementData.high;
  midlyEngagedCount.value = engagementData.middle;
  lowlyEngagedCount.value = engagementData.low;

  highlyEngagedPercentage.value = Math.ceil(
      (engagementData.high / userCount) * 100
  );
  midlyEngagedPercentage.value = Math.ceil(
      (engagementData.middle / userCount) * 100
  );
  lowlyEngagedPercentage.value = Math.ceil(
      (engagementData.low / userCount) * 100
  );
}

function onNewValue(newValue) {
  if (newValue === null) newValue = {};

  chartData.value = newValue;
  updateChart(Object.entries(newValue));
  updateTooltip(newValue);
}

function onChartDivMounted() {
  // Setup donut chart
  svg = select(`#donut_chart`)
      .append("svg")
      .attr("viewBox", `0 0 ${width} ${height}`);

  gElement = svg
      .append("g")
      .attr("transform", `translate(${width / 2},${height / 2})`);

  chartArc = arc()
      .innerRadius(innerRadius)
      .outerRadius(radius)
      .cornerRadius(cornerRadius);

  // Handle new data
  onNewValue(props.data);
  watch(
      () => props.data,
      (newValue, oldValue) => {
        onNewValue(newValue);
      }
  );
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
      .attr("class", `donut_chart`)
      .attr("fill", (d) => color(d.data[0]))
      .attr("d", chartArc)
      .each(function (d) {
        this._current = d;
      });

  // remove data not used
  gElement.exit().remove();
}
</script>

<template>
  <el-popover :width="300" class="tooltip" placement="top" trigger="hover">
    <template #reference>
      <div v-bind:id="'donut_chart'" @vue:mounted="onChartDivMounted"></div>
    </template>
    <div>
      <span
      ><b>{{ $t('charts.highly') }} {{ $t('analysis.tooltip-engaged') }}:</b> {{
          highlyEngagedPercentage
        }}% ({{ $t('general.user', highlyEngagedCount) }})</span
      >
      <br/>
      <span
      ><b>{{ $t('charts.maybe') }} {{ $t('analysis.tooltip-engaged') }}:</b> {{
          midlyEngagedPercentage
        }}% ({{ $t('general.user', midlyEngagedCount) }})</span
      >
      <br/>
      <span
      ><b>{{ $t('charts.lowly') }} {{ $t('analysis.tooltip-engaged') }}:</b> {{
          lowlyEngagedPercentage
        }}% ({{ $t('general.user', lowlyEngagedCount) }})</span
      >
    </div>
  </el-popover>
</template>

<style lang='scss'>
</style>