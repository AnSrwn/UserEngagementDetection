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
        <b>{{ $t('charts.positive-mood') }}:</b> {{ overallMoodPercentage }}%
      </div>
    </el-popover>
    <div class="mood-history"></div>
  </div>
</template>

<style lang="scss" scoped>
.current-mood {
  height: 100px;
  width: 100px;
  border-radius: 8px;
  background-color: v-bind(overallMoodColor);
}
</style>