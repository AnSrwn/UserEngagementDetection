<!-- Composition API -->
<script setup>
const props = defineProps({
  data: Object,
});

let barPercentage = ref("0%");
let barBackgroundColor = ref("#0aa849");
let tooltipText = ref("No data available");

function updateBar(percentageValue) {
  barPercentage.value = `${percentageValue}%`;
}

function updateColor(percentageValue) {
  let newColor = "#0aa849";

  if (percentageValue > 25) {
    newColor = "#e3df0b";
  }

  if (percentageValue > 50) {
    newColor = "#a11f0b";
  }

  barBackgroundColor.value = newColor;
}

function confusionDataToPercentage(confusionData) {
  let userCount = confusionData.high + confusionData.middle + confusionData.low;
  let confusion = confusionData.high + confusionData.middle / 2;

  if (userCount === 0) return 0;

  return Math.ceil((confusion / userCount) * 100);
}

function updateTooltip(confusionData) {
  let text = `Highly confused: ${confusionData.high}\n Midly confused: ${confusionData.middle} \n Not confused: ${confusionData.low}`;
  tooltipText.value = text;
}

function onNewValue(newValue) {
  if (newValue === null) return;

  let percentageValue = confusionDataToPercentage(newValue);

  if (percentageValue < 0) percentageValue = 0;
  if (percentageValue > 100) percentageValue = 100;

  updateBar(percentageValue);
  updateColor(percentageValue);
  updateTooltip(newValue);
}

function onChartDivMounted() {
  // Handle new data
  onNewValue(props.data);
  watch(
    () => props.data,
    (newValue, oldValue) => {
      onNewValue(newValue);
    }
  );
}
</script>

<template>
  <div id="bar-container">
    <div @vue:mounted="onChartDivMounted" id="bar-chart">
      <div id="bar" ref="bar"></div>
    </div>
    <div class="tooltip">
      <span id="tooltip-text">{{ tooltipText }}</span>
    </div>
  </div>
</template>

<style lang='scss'>
#bar-container {
  display: flex;
  flex-direction: row;
  align-items: center;
}

#bar-chart {
  display: flex;
  flex-direction: column-reverse;
  height: 100%;
  width: 100px;
  background-color: #ddd;
  border-radius: 8px;
}

#bar-chart:hover ~ .tooltip {
  visibility: visible;
  opacity: 1;
}

#bar {
  height: v-bind(barPercentage);
  background-color: v-bind(barBackgroundColor);
  transition: all 2s ease;
  border-radius: 8px;
}

.tooltip {
  visibility: hidden;
  width: 160px;
  height: fit-content;
  background-color: #555;
  color: #fff;
  text-align: center;
  border-radius: 6px;
  padding: 5px 0;
  z-index: 1;
  opacity: 0;
  transition: opacity 0.3s;
}
</style>
