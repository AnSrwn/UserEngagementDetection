<script>
import * as Plot from "@observablehq/plot";

export default {
  props: ["chartData"],
  watch: {
    chartData(newValue) {
      if (newValue.length) {
        const plot = Plot.plot({
          grid: true,
          marks: [
            Plot.frame(),
            Plot.ruleY([0]),
            Plot.line(newValue, { x: "time", y: "engagement" }),
          ],
        });
        const div = document.querySelector("#myplot");
        div.append(plot);
      }
    },
  },
};
</script>

<template>
  <div id="myplot"></div>
</template>

<style lang='scss'></style>