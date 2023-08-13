<script setup>
import {interpolateRgb} from "d3-interpolate";

const props = defineProps({
  currentData: Object,
  timelineData: Array
});

const emit = defineEmits(['timelineChanged'])

let numberOfUsers = ref(0);

let overallMoodPercentage = ref(0);
let overallMoodColor = ref();

let overallMoodTimelineData = ref([]);
let overallMoodTimelineDataWithPlaceholders = ref([]);
let maxTimelineItems = ref(350);

let moodHistoryElement = ref(null);

let moodHistoryItemWidth = ref('15px');

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

  overallMoodTimelineData.value.push({
    color: overallMoodColor.value,
    percentage: overallMoodPercentage,
    time: newValue.from_datetime
  });
  updateTimeline();
}

function updateTimeline() {
  let oldDataCount = overallMoodTimelineData.value.length - maxTimelineItems.value;
  if (oldDataCount > 0) {
    overallMoodTimelineData.value = overallMoodTimelineData.value.slice(oldDataCount);
  }

  let placeholderCount = maxTimelineItems.value - overallMoodTimelineData.value.length;
  let placeholderItems = placeholderCount > 0 ? new Array(placeholderCount) : [];
  overallMoodTimelineDataWithPlaceholders.value = overallMoodTimelineData.value.concat(placeholderItems);
}

function onNewTimelineData(newValue) {
  overallMoodTimelineData.value = newValue.map((item) => {
    let percentage = getOverallPercentage(item.avg_engagement, item.avg_boredom, item.avg_confusion, item.avg_frustration);
    let color = getMoodColor(percentage);
    return {color: color, percentage: percentage, time: item.from_datetime}
  })

  updateTimeline();
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

  adjustMaxTimelineItems()
  window.addEventListener("resize", onWindowSizeChange);
}

function adjustMaxTimelineItems() {
  let gap = 2;
  let defaultItemWidth = 15;
  let numberOfRows = 5

  let parentWidth = moodHistoryElement.value.offsetWidth;
  let maxRowItems = Math.floor(parentWidth / defaultItemWidth);
  maxTimelineItems.value = maxRowItems * numberOfRows;

  let newWidth = (parentWidth + 2 * gap - maxRowItems * gap) / maxRowItems;

  moodHistoryItemWidth.value = `${newWidth}px`

  emit('timelineChanged');
}

function onWindowSizeChange(event) {
  adjustMaxTimelineItems()
}

onDeactivated(() => {
  window.removeEventListener("resize", onWindowSizeChange);
})

onBeforeUnmount(() => {
  window.removeEventListener("resize", onWindowSizeChange);
})


</script>

<template>
  <div @vue:mounted="onChartDivMounted">
    <el-popover :width="190" class="tooltip" placement="top" trigger="hover">
      <template #reference>
        <div class="current-mood"></div>
      </template>
      <div class="tooltip-content">
        <b>{{ $t('charts.tooltip-overall-mood') }}:</b> {{ overallMoodPercentage }}%
      </div>
    </el-popover>
    <el-popover :width="190" class="tooltip" placement="top" trigger="hover">
      <template #reference>
        <div ref="moodHistoryElement" class="mood-history">
          <div v-for="item in overallMoodTimelineDataWithPlaceholders"
               :style="{ 'background-color': item ? item.color : '#D3D3D3'}"
               class="mood-history-item"/>
        </div>
      </template>
      <div class="tooltip-content" style="white-space: normal; word-break: keep-all; word-wrap: break-word;">
        {{ $t('charts.tooltip-overall-mood-timeline') }}
      </div>
    </el-popover>
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
  width: v-bind(moodHistoryItemWidth);
  border-radius: 4px;
  background-color: lightgray;
}
</style>