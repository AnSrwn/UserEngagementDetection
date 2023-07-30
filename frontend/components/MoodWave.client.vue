<!-- Composition API -->
<script setup>
import { interpolateRgb } from "d3-interpolate";

const props = defineProps({
  data: Object,
});

let numberOfUsers = ref(0);
let overallMoodPercentage = ref(0);
let engagementPercentage = ref(0);
let boredomPercentage = ref(0);
let confusionPercentage = ref(0);
let frustrationPercentage = ref(0);

let overallMoodColor = ref();

function calculatePercentage(value) {
  return Math.ceil((value / numberOfUsers.value) * 100);
}

function setAllPercentages(newValue) {
  engagementPercentage.value = calculatePercentage(
    newValue.engagement.high + newValue.engagement.middle / 2
  );
  boredomPercentage.value = calculatePercentage(
    newValue.boredom.high + newValue.boredom.middle / 2
  );
  confusionPercentage.value = calculatePercentage(
    newValue.confusion.high + newValue.confusion.middle / 2
  );
  frustrationPercentage.value = calculatePercentage(
    newValue.frustration.high + newValue.frustration.middle / 2
  );

  overallMoodPercentage.value = Math.ceil(
    (engagementPercentage.value +
      (100 - boredomPercentage.value) +
      (100 - confusionPercentage.value) +
      (100 - frustrationPercentage.value)) /
      4
  );
}

function setColors() {
  overallMoodColor.value = interpolateRgb(
    // "rgb(0, 0, 0)",
    // "rgb(238, 198, 31)"
    "rgb(0, 0, 0)",
    "rgb(255, 225, 99)"
  )(overallMoodPercentage.value / 100);

  document
    .getElementById("path-1")
    .setAttribute("fill", overallMoodColor.value);

  let engagementColor = interpolateRgb(
    // "rgb(22, 27, 112)",
    // "rgb(254, 88, 33)"
    "rgb(25, 29, 87)",
    "rgb(247, 121, 79)"
  )(engagementPercentage.value / 100);

  let boredomColor = interpolateRgb(
    // "rgb(217, 17, 17)",
    // "rgb(128, 128, 128)"
    "rgb(252, 139, 139)",
    "rgb(54, 54, 54)"
  )(boredomPercentage.value / 100);

  let confusionColor = interpolateRgb(
    // "rgb(128, 0, 128)",
    // "rgb(64, 224, 208)"
    "rgb(204, 137, 204)",
    "rgb(2, 66, 60)"
  )(confusionPercentage.value / 100);

  let frustrationColor = interpolateRgb(
    // "rgb(255, 255, 0)"
    // "rgb(135, 20, 16)",
    // "rgb(255, 165, 0)"
    "rgb(252, 199, 101)",
    "rgb(79, 6, 3)"
  )(frustrationPercentage.value / 100);

  document.getElementById("path-2").setAttribute("fill", engagementColor);

  document.getElementById("path-3").setAttribute("fill", confusionColor);

  document.getElementById("path-4").setAttribute("fill", boredomColor);

  document.getElementById("path-5").setAttribute("fill", frustrationColor);
}

function onNewValue(newValue) {
  if (newValue === null) return;

  numberOfUsers.value = newValue.numberOfUsers;
  setAllPercentages(newValue);
  setColors();
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
  <div @vue:mounted="onChartDivMounted" id="wave-chart">
    <div id="overall-mood"></div>
    <div id="waves">
      <svg
        id="waves-svg"
        class="waves-svg"
        viewBox="0 0 900 150"
        xmlns="http://www.w3.org/2000/svg"
        xmlns:xlink="http://www.w3.org/1999/xlink"
        version="1.1"
      >
        <path
          id="path-5"
          d="M0 129L21.5 129.2C43 129.3 86 129.7 128.8 131C171.7 132.3 214.3 134.7 257.2 128.2C300 121.7 343 106.3 385.8 106.5C428.7 106.7 471.3 122.3 514.2 127C557 131.7 600 125.3 642.8 117.8C685.7 110.3 728.3 101.7 771.2 100.3C814 99 857 105 878.5 108L900 111L900 0L878.5 0C857 0 814 0 771.2 0C728.3 0 685.7 0 642.8 0C600 0 557 0 514.2 0C471.3 0 428.7 0 385.8 0C343 0 300 0 257.2 0C214.3 0 171.7 0 128.8 0C86 0 43 0 21.5 0L0 0Z"
          fill="#77fa69"
        ></path>
        <path
          id="path-4"
          d="M0 96L21.5 92.5C43 89 86 82 128.8 85.7C171.7 89.3 214.3 103.7 257.2 103.2C300 102.7 343 87.3 385.8 87.5C428.7 87.7 471.3 103.3 514.2 109.5C557 115.7 600 112.3 642.8 111.2C685.7 110 728.3 111 771.2 106.2C814 101.3 857 90.7 878.5 85.3L900 80L900 0L878.5 0C857 0 814 0 771.2 0C728.3 0 685.7 0 642.8 0C600 0 557 0 514.2 0C471.3 0 428.7 0 385.8 0C343 0 300 0 257.2 0C214.3 0 171.7 0 128.8 0C86 0 43 0 21.5 0L0 0Z"
          fill="#b1cc23"
        ></path>
        <path
          id="path-3"
          d="M0 59L21.5 58.7C43 58.3 86 57.7 128.8 63.5C171.7 69.3 214.3 81.7 257.2 84.3C300 87 343 80 385.8 74.7C428.7 69.3 471.3 65.7 514.2 62.8C557 60 600 58 642.8 60.3C685.7 62.7 728.3 69.3 771.2 71.8C814 74.3 857 72.7 878.5 71.8L900 71L900 0L878.5 0C857 0 814 0 771.2 0C728.3 0 685.7 0 642.8 0C600 0 557 0 514.2 0C471.3 0 428.7 0 385.8 0C343 0 300 0 257.2 0C214.3 0 171.7 0 128.8 0C86 0 43 0 21.5 0L0 0Z"
          fill="#c89c00"
        ></path>
        <path
          id="path-2"
          d="M0 33L21.5 38.5C43 44 86 55 128.8 55.5C171.7 56 214.3 46 257.2 41.2C300 36.3 343 36.7 385.8 41.7C428.7 46.7 471.3 56.3 514.2 55.8C557 55.3 600 44.7 642.8 40.3C685.7 36 728.3 38 771.2 43.7C814 49.3 857 58.7 878.5 63.3L900 68L900 0L878.5 0C857 0 814 0 771.2 0C728.3 0 685.7 0 642.8 0C600 0 557 0 514.2 0C471.3 0 428.7 0 385.8 0C343 0 300 0 257.2 0C214.3 0 171.7 0 128.8 0C86 0 43 0 21.5 0L0 0Z"
          fill="#ce6a03"
        ></path>
        <path
          id="path-1"
          d="M0 44L21.5 41.7C43 39.3 86 34.7 128.8 34.5C171.7 34.3 214.3 38.7 257.2 39.8C300 41 343 39 385.8 37.2C428.7 35.3 471.3 33.7 514.2 33C557 32.3 600 32.7 642.8 30.3C685.7 28 728.3 23 771.2 21.2C814 19.3 857 20.7 878.5 21.3L900 22L900 0L878.5 0C857 0 814 0 771.2 0C728.3 0 685.7 0 642.8 0C600 0 557 0 514.2 0C471.3 0 428.7 0 385.8 0C343 0 300 0 257.2 0C214.3 0 171.7 0 128.8 0C86 0 43 0 21.5 0L0 0Z"
          fill="#c72e24"
        ></path>
      </svg>
    </div>
  </div>
</template>

<style lang='scss'>
#overall-mood {
  height: 50px;
  width: 100%;
  background-color: v-bind(overallMoodColor);
}
</style>