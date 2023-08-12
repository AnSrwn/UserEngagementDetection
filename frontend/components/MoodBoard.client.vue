<script setup>
import {interpolateRgb} from "d3-interpolate";

const props = defineProps({
  currentData: Object,
});

let numberOfUsers = ref(0);

let overallMoodPercentage = ref(0);
let overallMoodColor = ref();

function calculatePercentage(value) {
  return Math.ceil((value / numberOfUsers.value) * 100);
}

function setOverallMoodPercentage(newValue) {
  let engagementPercentage = calculatePercentage(
      newValue.engagement.high + newValue.engagement.middle / 2
  );
  let boredomPercentage = calculatePercentage(
      newValue.boredom.high + newValue.boredom.middle / 2
  );
  let confusionPercentage = calculatePercentage(
      newValue.confusion.high + newValue.confusion.middle / 2
  );
  let frustrationPercentage = calculatePercentage(
      newValue.frustration.high + newValue.frustration.middle / 2
  );

  overallMoodPercentage.value = Math.ceil(
      (engagementPercentage +
          (100 - boredomPercentage) +
          (100 - confusionPercentage) +
          (100 - frustrationPercentage)) /
      4
  );
}

function setCurrentMoodColor() {
  if (overallMoodPercentage.value < 50.0) {
    let partPercentage = overallMoodPercentage.value * 2;
    overallMoodColor.value = interpolateRgb(
        "rgb(161, 31, 11)",
        "rgb(227, 223, 11)"
    )(partPercentage / 100);
  } else {
    let partPercentage = overallMoodPercentage.value * 2 - 100;
    overallMoodColor.value = interpolateRgb(
        "rgb(227, 223, 11)",
        "rgb(10, 168, 73)"
    )(partPercentage / 100);
  }
}

function onNewValue(newValue) {
  if (newValue === null) return;

  numberOfUsers.value = newValue.visible_users;
  setOverallMoodPercentage(newValue);
  setCurrentMoodColor();
}

function onChartDivMounted() {
  // Handle new data
  onNewValue(props.currentData);
  watch(
      () => props.currentData,
      (newValue, oldValue) => {
        onNewValue(newValue);
      }
  );
}
</script>

<template>
  <div @vue:mounted="onChartDivMounted">
    <el-popover :width="170" class="tooltip" placement="top" trigger="hover">
      <template #reference>
        <div class="current-mood"></div>
      </template>
      <div class="tooltip-content">
        <b>{{ $t('charts.tooltip-overall-mood') }}:</b> {{ overallMoodPercentage }}%
      </div>
    </el-popover>
    <div class="mood-history" >
        <div class="mood-history-item" v-for="item in new Array(300)" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.current-mood {
  height: 60px;
  width: 100%;
  border-radius: 8px;
  background-color: v-bind(overallMoodColor);
  margin-bottom: 15px;
}

.mood-history {
  display: flex;
  flex-direction: column;
  flex-wrap: wrap;
  gap: 2px;
  max-height: 85px;
  width: 100%;
}

.mood-history-item {
  height: 15px;
  width: 15px;
  border-radius: 4px;
  background-color: lightgray;
}
</style>