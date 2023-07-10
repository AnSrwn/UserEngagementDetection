<!-- Composition API -->
<script setup>
import * as Plot from "@observablehq/plot";
// import * as d3 from "d3";
import { transition } from "d3-transition";
import { line, curveCatmullRom } from "d3-shape";
import { scaleLinear, scaleUtc } from "d3-scale";
import { axisBottom, axisLeft } from "d3-axis";
import { timeFormat } from "d3-time-format";
import { select, create } from "d3-selection";
import { extent, max } from "d3-array";
import { ref, defineExpose } from "vue";

function createChart(data) {
  // Declare the chart dimensions and margins.
  const width = 928;
  const height = 500;
  const marginTop = 20;
  const marginRight = 30;
  const marginBottom = 30;
  const marginLeft = 40;

  // Declare the x (horizontal position) scale.
  const x = scaleUtc(
    extent(data, (d) => d.time),
    [marginLeft, width - marginRight]
  );

  // Declare the y (vertical position) scale.
  const y = scaleLinear(
    [0, max(data, (d) => d.engagement)],
    [height - marginBottom, marginTop]
  );

  // Declare the line generator.
  const lineGenerator = line()
    .x((d) => x(d.time))
    .y((d) => y(d.engagement));
    // .curve(curveCatmullRom.alpha(0.5));

  // Create the SVG container.
  const svg = create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .attr("style", "max-width: 100%; height: auto; height: intrinsic;");

  // Add the x-axis.
  var format = timeFormat("%X");
  svg
    .append("g")
    .attr("transform", `translate(0,${height - marginBottom})`)
    .call(
      axisBottom(x).tickFormat(format)
      // .ticks(width / 80)
      // .tickSizeOuter(0)
    );

  // Add the y-axis, remove the domain line, add grid lines and a label.
  svg
    .append("g")
    .attr("transform", `translate(${marginLeft},0)`)
    .call(axisLeft(y).ticks(height / 40))
    .call((g) => g.select(".domain").remove())
    .call((g) =>
      g
        .selectAll(".tick line")
        .clone()
        .attr("x2", width - marginLeft - marginRight)
        .attr("stroke-opacity", 0.1)
    )
    .call((g) =>
      g
        .append("text")
        .attr("x", -marginLeft)
        .attr("y", 10)
        .attr("fill", "currentColor")
        .attr("text-anchor", "start")
        .text("↑ Engagement")
    );

  // Append a path for the line.
  svg
    .append("path")
    .attr("fill", "none")
    .attr("stroke", "steelblue")
    .attr("stroke-width", 1.5);

  svg.append("path").attr("class", "line").attr("d", lineGenerator(data));

  return svg.node();
}

let isInitial = true;
const chartDiv = ref(null);
// defineExpose({ chartDiv })
let chartData = ref([]);

// const { chartData } = defineProps(['chartData'])
const props = defineProps({
  data: Array,
});

onMounted(() => {
  watch(
    () => props.data,
    (newValue, oldValue) => {
      chartData.value = newValue;

      if (newValue !== undefined && newValue.length) {
        // const plot = Plot.plot({
        //   grid: true,
        //   marks: [
        //     Plot.frame(),
        //     Plot.ruleY([0]),
        //     Plot.line(newValue, { x: "time", y: "engagement" }),
        //   ],
        // });

        // const plot = createChart(newValue);
        // chartDiv.value.append(plot);

        if (isInitial) {
          isInitial = false;
          const plot = createChart(newValue);
          chartDiv.value.append(plot);
        } else {
          const width = 928;
          const height = 500;
          const marginTop = 20;
          const marginRight = 30;
          const marginBottom = 30;
          const marginLeft = 40;

          // Declare the x (horizontal position) scale.
          const x = scaleUtc(
            extent(newValue, (d) => d.time),
            [marginLeft, width - marginRight]
          );

          // Declare the y (vertical position) scale.
          const y = scaleLinear(
            [0, max(newValue, (d) => d.engagement)],
            [height - marginBottom, marginTop]
          );

          // TODO: https://plnkr.co/edit/ZEQlzJtHKcVdcAWmuwxA?p=preview&preview
          const plot = select("#myplot").transition();
          plot
            .select("line")
            .duration(750)
            .attr(
              "d",
              line(newValue)
                .x((d) => x(d.time))
                .y((d) => y(d.engagement))
            );
        }
      }
    }
  );
});

// export default {
//   props: {
//     chartData: Array,
//   },
//   // data() {
//   //     return {
//   //       engagementData: []
//   //     }
//   // },
//   watch: {
//     chartData: {
//       handler(newValue, oldValue) {
//         console.log(newValue);
//         // this.engagementData = newValue;
//         if (newValue !== undefined && newValue.length) {
//           // const plot = Plot.plot({
//           //   grid: true,
//           //   marks: [
//           //     Plot.frame(),
//           //     Plot.ruleY([0]),
//           //     Plot.line(newValue, { x: "time", y: "engagement" }),
//           //   ],
//           // });

//           if (isInitial) {
//             isInitial = false;
//             const plot = createChart(newValue);
//             const div = document.querySelector("#myplot");
//             div.append(plot);
//           } else {
//             console.log("hello");
//             // TODO: https://plnkr.co/edit/ZEQlzJtHKcVdcAWmuwxA?p=preview&preview
//             const plot = select("#myplot").transition();
//             plot.select(".line").duration(750).attr("d", line(newValue));
//           }
//         }
//       },
//       deep: true,
//     },
//   },
// };
</script>

<template>
  <div>
    <div>Engagement: {{ chartData }}</div>
    <div ref="chartDiv" id="myplot"></div>
  </div>
</template>

<style lang='scss'></style>