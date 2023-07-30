<!-- Composition API -->
<script setup>
const props = defineProps({
  data: Object,
});

let barPercentage = ref("0%");
let barBackgroundColor = ref("#0aa849");
let highlyConfusedCount = ref(0);
let midlyConfusedCount = ref(0);
let lowlyConfusedCount = ref(0);
let highlyConfusedPercentage = ref(0);
let midlyConfusedPercentage = ref(0);
let lowlyConfusedPercentage = ref(0);

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

function getUserCount(confusionData) {
  return confusionData.high + confusionData.middle + confusionData.low;
}

function confusionDataToPercentage(confusionData) {
  let userCount = getUserCount(confusionData);
  let confusion = confusionData.high + confusionData.middle / 2;

  if (userCount === 0) return 0;

  return Math.ceil((confusion / userCount) * 100);
}

function updateTooltip(confusionData) {
  let userCount = getUserCount(confusionData);
  highlyConfusedCount.value = confusionData.high;
  midlyConfusedCount.value = confusionData.middle;
  lowlyConfusedCount.value = confusionData.low;

  highlyConfusedPercentage.value = Math.ceil(
    (confusionData.high / userCount) * 100
  );
  midlyConfusedPercentage.value = Math.ceil(
    (confusionData.middle / userCount) * 100
  );
  lowlyConfusedPercentage.value = Math.ceil(
    (confusionData.low / userCount) * 100
  );
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
  <el-popover placement="right" :width="fit - content" trigger="hover">
    <template #reference>
      <div @vue:mounted="onChartDivMounted" id="bar-chart">
        <div id="bar" ref="bar"></div>
      </div>
    </template>
    <div>
      <span
        ><b>Highly Confused:</b> {{ highlyConfusedPercentage }} % ({{
          highlyConfusedCount
        }}
        Users)</span
      >
      <br />
      <span
        ><b>Midly Confused:</b> {{ midlyConfusedPercentage }} % ({{
          midlyConfusedCount
        }}
        Users)</span
      >
      <br />
      <span
        ><b>Lowly Confused:</b> {{ lowlyConfusedPercentage }} % ({{
          lowlyConfusedCount
        }}
        Users)</span
      >
    </div>
  </el-popover>
</template>

<style lang='scss'>
#bar-chart {
  display: flex;
  flex-direction: column-reverse;
  height: 450px;
  width: 100px;
  background-color: #ddd;
  border-radius: 8px;
}

#bar {
  height: v-bind(barPercentage);
  background-color: v-bind(barBackgroundColor);
  transition: all 2s ease;
  border-radius: 8px;
}
</style>
