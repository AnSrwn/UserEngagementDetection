<!-- Composition API -->
<script setup>
const props = defineProps({
  data: Object,
  tooltipText: String,
});

let barPercentage = ref("0%");
let barBackgroundColor = ref("#0aa849");
let highlyCount = ref(0);
let midlyCount = ref(0);
let lowlyCount = ref(0);
let highlyPercentage = ref(0);
let midlyPercentage = ref(0);
let lowlyPercentage = ref(0);

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

function getUserCount(data) {
  return data.high + data.middle + data.low;
}

function dataToPercentage(data) {
  let userCount = getUserCount(data);
  let relevantUsers = data.high + data.middle / 2;

  if (userCount === 0) return 0;

  return Math.ceil((relevantUsers / userCount) * 100);
}

function updateTooltip(data) {
  let userCount = getUserCount(data);
  highlyCount.value = data.high;
  midlyCount.value = data.middle;
  lowlyCount.value = data.low;

  highlyPercentage.value = Math.ceil(
      (data.high / userCount) * 100
  );
  midlyPercentage.value = Math.ceil(
      (data.middle / userCount) * 100
  );
  lowlyPercentage.value = Math.ceil(
      (data.low / userCount) * 100
  );
}

function onNewValue(newValue) {
  if (newValue === null) return;

  let percentageValue = dataToPercentage(newValue);

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
  <el-popover class="tooltip" placement="top" trigger="hover">
    <template #reference>
      <div id="bar-chart" @vue:mounted="onChartDivMounted">
        <div id="bar" ref="bar"></div>
      </div>
    </template>
    <div>
      <span
      ><b>{{ $t('charts.highly') }} {{ props.tooltipText }}:</b> {{
          highlyPercentage
        }}% ({{ $t('general.user', highlyCount) }})</span
      >
      <br/>
      <span
      ><b>{{ $t('charts.maybe') }} {{ props.tooltipText }}:</b> {{
          midlyPercentage
        }}% ({{ $t('general.user', midlyCount) }})</span
      >
      <br/>
      <span
      ><b>{{ $t('charts.lowly') }} {{ props.tooltipText }}:</b> {{
          lowlyPercentage
        }}% ({{ $t('general.user', lowlyCount) }})</span
      >
    </div>
  </el-popover>
</template>

<style lang='scss'>
#bar-chart {
  width: 100%;
  height: 80px;
  display: flex;
  flex-direction: column-reverse;
  background-color: #ddd;
  border-radius: 8px;
}

#bar {
  width: v-bind(barPercentage);
  height: 100%;
  background-color: v-bind(barBackgroundColor);
  transition: all 2s ease;
  border-radius: 8px;
}

.tooltip {
  width: fit-content;
}
</style>
