<script setup>
import {useApiFetch} from "~/composables/useApiFetch";
import {toTimelineEngagementClientItem} from "~/composables/serverToClient";
import {CircleCloseFilled, Setting} from '@element-plus/icons-vue'


const currentIntervalSeconds = ref(5);
const timelineIntervalSeconds = ref(60);

const openCollapseViews = ref([])
const settingsVisible = ref(false);

let connectedUsers = ref();
let visibleUsers = ref();

let currentAllData = ref();
let currentEngagement = ref();
let currentBoredom = ref();
let currentConfusion = ref();
let currentFrustration = ref();

let timelineAllData = ref([]);
let timelineEngagement = ref([]);
let timelineBoredom = ref([]);
let timelineConfusion = ref([]);
let timelineFrustration = ref([]);

let timelinePeriod = ref(30); // minutes

const getCurrentEngagement = async () => {
  let params = () => {
    return {interval: currentIntervalSeconds.value}
  }

  const {data} = await useApiFetch(`engagement/average/simple`, {
    query: params()
  });

  if (data.value !== null) {
    currentAllData = data.value;

    connectedUsers.value = data.value.connections;
    visibleUsers.value = data.value.visible_users;

    currentEngagement.value = data.value.engagement;
    currentBoredom.value = data.value.boredom;
    currentConfusion.value = data.value.confusion;
    currentFrustration.value = data.value.frustration;
  }
}

const getTimelinePeriodEngagement = async () => {
  let params = () => {
    let earliestFromDatetime = new Date(((new Date()).getTime() - timelinePeriod.value * 60000));
    let fromDatetime = earliestFromDatetime.toISOString();
    let toDatetime = (new Date()).toISOString();

    return {from_datetime: fromDatetime, to_datetime: toDatetime, interval: timelineIntervalSeconds.value}
  }

  const {data} = await useApiFetch('engagement/average/percentage/period', {
    query: params(),
    transform: (data) => {
      return data.map((item) => toTimelineEngagementClientItem(item));
    }
  });

  setTimelineData(data);
}

const getTimelinePointEngagement = async () => {
  let params = () => {
    return {interval: timelineIntervalSeconds.value}
  }

  const {data} = await useApiFetch(`engagement/average/percentage`, {
    query: params(),
    transform: (data) => {
      return data.map((item) => toTimelineEngagementClientItem(item));
    },
  });

  // Remove expired data
  let earliestFromDatetime = new Date(((new Date()).getTime() - timelinePeriod.value * 60000));
  let filtered = timelineAllData.value.filter((item) => item.from_datetime.getTime() > earliestFromDatetime.getTime())

  if (data.value !== null && data.value[0].from_datetime !== null) {
    filtered = filtered.concat(data.value);
  }

  setTimelineData(filtered);
}

function setTimelineData(data) {
  timelineAllData.value = data.value;
  timelineEngagement.value = data.value.map(item => {
    return {time: item.from_datetime, percentage: item.avg_engagement}
  });
  timelineBoredom.value = data.value.map(item => {
    return {time: item.from_datetime, percentage: item.avg_boredom}
  });
  timelineConfusion.value = data.value.map(item => {
    return {time: item.from_datetime, percentage: item.avg_confusion}
  });
  timelineFrustration.value = data.value.map(item => {
    return {time: item.from_datetime, percentage: item.avg_frustration}
  });
}


let currentInterval;
let timelineInterval

onMounted(async () => {
  await fetchOnMount(getCurrentEngagement);
  await fetchOnMount(getTimelinePeriodEngagement);
  currentInterval = setInterval(getCurrentEngagement, currentIntervalSeconds.value * 1000);
  timelineInterval = setInterval(getTimelinePointEngagement, timelineIntervalSeconds.value * 1000);
})

onDeactivated(() => {
  clearInterval(currentInterval);
  clearInterval(timelineInterval);
})

onBeforeUnmount(() => {
  clearInterval(currentInterval);
  clearInterval(timelineInterval);
})

function onCurrentIntervalSecondsChange() {
  clearInterval(currentInterval);
  currentInterval = setInterval(getCurrentEngagement, currentIntervalSeconds.value * 1000);
}

function onTimelineIntervalSecondsChange() {
  clearInterval(timelineInterval);
  timelineInterval = setInterval(getTimelinePointEngagement, timelineIntervalSeconds.value * 1000);
}
</script>

<template>
  <div>
    <div class="headline">
      <h1>{{ $t('analysis.title') }}</h1>
      <el-button :icon="Setting" type="primary" @click="settingsVisible = true">{{
          $t('analysis.settings')
        }}
      </el-button>
    </div>
    <client-only>
      <el-drawer v-model="settingsVisible" :show-close="false">
        <template #header="{ close, titleId, titleClass }">
          <h2>{{ $t('analysis.settings') }}</h2>
          <el-button type="danger" @click="close">
            <el-icon class="el-icon--left">
              <CircleCloseFilled/>
            </el-icon>
            {{ $t('general.close') }}
          </el-button>
        </template>
        Refresh Interval for live data (in seconds):
        <el-input-number
            v-model="currentIntervalSeconds"
            :min="3"
            :max="300"
            @change="onCurrentIntervalSecondsChange"
        />
        <br />
        Refresh Interval for timeline data (in seconds):
        <el-input-number
            v-model="timelineIntervalSeconds"
            :min="10"
            :max="300"
            @change="onTimelineIntervalSecondsChange"
        />
        <br />
        Timeline complete period (in minutes):
        <el-input-number
            v-model="timelinePeriod"
            :min="15"
            :max="120"
        />
      </el-drawer>
      <div class="info-container">
        <el-card class="info-card">
          <div class="large-text">{{ connectedUsers }}</div>
          <div>{{ $t('analysis.info-connected-users') }}</div>
        </el-card>
        <el-card class="info-card">
          <div class="large-text">{{ visibleUsers }}</div>
          <div>{{ $t('analysis.info-visible-users') }}</div>
        </el-card>
      </div>
      <el-divider/>
      <MoodWave v-if="visibleUsers > 0" :data="currentAllData"/>
      <div class="charts-container">
        <el-card class="engagement-card">
          <template #header>
            <h2>{{ $t('analysis.engagement') }}</h2>
          </template>
          <DonutChart v-if="visibleUsers > 0" :data="currentEngagement"/>
          <div v-else>{{ $t('analysis.no-data') }}</div>
          <el-collapse v-model="openCollapseViews" class="collapse-view">
            <el-collapse-item name="timelineEngagement">
              <template #title>
                <h3>{{ $t('analysis.timeline-title') }}</h3>
              </template>
              <LineChart v-if="timelineEngagement.length > 0" :data="timelineEngagement"/>
            </el-collapse-item>
          </el-collapse>
        </el-card>
        <div class="bar-chart-container">
          <el-card class="bar-card">
            <template #header>
              <h2>{{ $t('analysis.confusion') }}</h2>
            </template>
            <BarChart
                v-if="visibleUsers > 0"
                :data="currentConfusion"
                :tooltipText="$t('analysis.tooltip-confused')"
                class="bar-chart"
            />
            <div v-else>{{ $t('analysis.no-data') }}</div>
            <el-collapse v-model="openCollapseViews" class="collapse-view">
              <el-collapse-item name="timelineConfusion">
                <template #title>
                  <h3>{{ $t('analysis.timeline-title') }}</h3>
                </template>
                <LineChart v-if="timelineConfusion.length > 0" :data="timelineConfusion"/>
              </el-collapse-item>
            </el-collapse>
          </el-card>
          <el-card class="bar-card">
            <template #header>
              <h2>{{ $t('analysis.boredom') }}</h2>
            </template>
            <BarChart
                v-if="visibleUsers > 0"
                :data="currentBoredom"
                :tooltipText="$t('analysis.tooltip-bored')"
                class="bar-chart"
            />
            <div v-else>{{ $t('analysis.no-data') }}</div>
            <el-collapse v-model="openCollapseViews" class="collapse-view">
              <el-collapse-item name="timelineBoredom">
                <template #title>
                  <h3>{{ $t('analysis.timeline-title') }}</h3>
                </template>
                <LineChart v-if="timelineBoredom.length > 0" :data="timelineBoredom"/>
              </el-collapse-item>
            </el-collapse>
          </el-card>
          <el-card class="bar-card">
            <template #header>
              <h2>{{ $t('analysis.frustration') }}</h2>
            </template>
            <BarChart
                v-if="visibleUsers > 0"
                :data="currentFrustration"
                :tooltipText="$t('analysis.tooltip-frustrated')"
                class="bar-chart"
            />
            <div v-else>{{ $t('analysis.no-data') }}</div>
            <el-collapse v-model="openCollapseViews" class="collapse-view">
              <el-collapse-item name="timelineFrustration">
                <template #title>
                  <h3>{{ $t('analysis.timeline-title') }}</h3>
                </template>
                <LineChart v-if="timelineFrustration.length > 0" :data="timelineFrustration"/>
              </el-collapse-item>
            </el-collapse>
          </el-card>
        </div>
      </div>
    </client-only>
  </div>
</template>

<style lang='scss' scoped>
.headline {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: baseline;
}

.info-container {
  display: flex;
  flex-direction: row;
  gap: 20px 20px;
}

.info-card {
  width: fit-content;
  height: fit-content;

  .large-text {
    font-weight: bold;
    font-size: 2.5em;
  }
}

.charts-container {
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;
  justify-content: space-between;
  height: 500px;
  gap: 30px 30px;
}

.collapse-view {
  margin-top: 20px;
}

.engagement-card {
  max-width: 560px;
  min-width: 400px;
  flex-grow: 1;
  height: fit-content;
  padding-bottom: 20px;
}

@media only screen and (max-width: 400px) {
  .engagement-card {
    min-width: 100%;
  }
}

.bar-chart-container {
  display: flex;
  max-width: 560px;
  min-width: 400px;
  flex-direction: column;
  flex-grow: 1;
  gap: 30px 30px;
  padding-bottom: 20px;
}

@media only screen and (max-width: 400px) {
  .bar-chart-container {
    min-width: 100%;
  }
}

.bar-card {
  width: 100%;
  height: fit-content;

  .bar-chart {
    width: 100%;
    height: fit-content;
  }
}
</style>