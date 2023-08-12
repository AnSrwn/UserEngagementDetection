<script setup>
import {interpolateRgb} from "d3-interpolate";

const props = defineProps({
  currentData: Object,
  timelineData: Array
});

let numberOfUsers = ref(0);

let overallMoodPercentage = ref(0);
let overallMoodColor = ref();

let overallMoodTimelineData = ref([])

function calculatePercentage(value) {
  return Math.ceil((value / numberOfUsers.value) * 100);
}

function getOverallPercentage(engagementPercentage, boredomPercentage, confusionPercentage, frustrationPercentage) {
  return Math.ceil(
      (engagementPercentage +
          (100 - boredomPercentage) +
          (100 - confusionPercentage) +
          (100 - frustrationPercentage)) /
      4
  );
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

  overallMoodPercentage.value = getOverallPercentage(engagementPercentage, boredomPercentage, confusionPercentage, frustrationPercentage);
}

function getMoodColor(percentage) {
  if (percentage < 50.0) {
    let partPercentage = percentage * 2;
    return interpolateRgb(
        "rgb(161, 31, 11)",
        "rgb(227, 223, 11)"
    )(partPercentage / 100);
  } else {
    let partPercentage = percentage * 2 - 100;
    return interpolateRgb(
        "rgb(227, 223, 11)",
        "rgb(10, 168, 73)"
    )(partPercentage / 100);
  }
}

function setCurrentMoodColor() {
  overallMoodColor.value = getMoodColor(overallMoodPercentage.value);
}

function onNewCurrentData(newValue) {
  if (newValue === null) return;

  numberOfUsers.value = newValue.visible_users;
  setOverallMoodPercentage(newValue);
  setCurrentMoodColor();
}

function onNewTimelineData(newValue) {
  let moodItems = newValue.map((item) => {
    let percentage = getOverallPercentage(item.avg_engagement, item.avg_boredom, item.avg_confusion, item.avg_frustration);
    let color = getMoodColor(percentage);
    return {color: color, percentage: percentage, time: item.from_datetime}
  })

  let missingItemsCount = 350 - moodItems.length;
  console.log(missingItemsCount)
  let missingItems = new Array(missingItemsCount)
  overallMoodTimelineData.value = moodItems.concat(missingItems);
}

function onChartDivMounted() {
  // Handle new data
  onNewCurrentData(props.currentData);
  watch(
      () => props.currentData,
      (newValue, oldValue) => {
        onNewCurrentData(newValue);
      }
  );
  watch(
      () => props.timelineData,
      (newValue, oldValue) => {
        onNewTimelineData(newValue);
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
    <div class="mood-history">
      <div v-for="item in overallMoodTimelineData" :style="{ 'background-color': item ? item.color : '#D3D3D3'}"
           class="mood-history-item"/>
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
  align-content: flex-start;
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