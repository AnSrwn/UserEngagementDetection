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

let isCurrentDataEmpty = ref(true);
let currentDataOutdated = ref(false);
let currentAllData = ref();
let currentEngagement = ref();
let currentBoredom = ref();
let currentConfusion = ref();
let currentFrustration = ref();

let timelineOutdated = ref(false)
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
    connectedUsers.value = data.value.connections;
    visibleUsers.value = data.value.visible_users;

    currentDataOutdated.value = connectedUsers.value > 0 && visibleUsers.value < 1 && data.value.engagement.high === 0 && data.value.engagement.middle === 0 && data.value.engagement.low === 0

    if (currentDataOutdated.value) {
      // do not change visualization if data is outdated
      return
    }

    currentAllData.value = data.value;
    currentEngagement.value = data.value.engagement;
    currentBoredom.value = data.value.boredom;
    currentConfusion.value = data.value.confusion;
    currentFrustration.value = data.value.frustration;

    isCurrentDataEmpty.value = currentEngagement.value.high === 0 && currentEngagement.value.middle === 0 && currentEngagement.value.low === 0;
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

  setTimelineData(data.value);
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

  timelineOutdated.value = data.value === null || data.value[0].from_datetime === null;

  if (timelineOutdated.value) {
    // do not change visualization if data is outdated
    return
  }

  // Remove expired data
  let earliestFromDatetime = new Date(((new Date()).getTime() - timelinePeriod.value * 60000));
  let filtered = timelineAllData.value !== undefined && timelineAllData.value !== null ? (timelineAllData.value.filter((item) => item.from_datetime.getTime() < earliestFromDatetime.getTime())) : []

  filtered = filtered.concat(data.value);

  setTimelineData(filtered);
}

function setTimelineData(data) {
  timelineAllData.value = data;
  timelineEngagement.value = data.map(item => {
    return {time: item.from_datetime, percentage: item.avg_engagement}
  });
  timelineBoredom.value = data.map(item => {
    return {time: item.from_datetime, percentage: item.avg_boredom}
  });
  timelineConfusion.value = data.map(item => {
    return {time: item.from_datetime, percentage: item.avg_confusion}
  });
  timelineFrustration.value = data.map(item => {
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
  getCurrentEngagement();
}

function onTimelineIntervalSecondsChange() {
  clearInterval(timelineInterval);
  timelineInterval = setInterval(getTimelinePointEngagement, timelineIntervalSeconds.value * 1000);
  getTimelinePeriodEngagement();
}

function onTimelinePeriodChange() {
  getTimelinePeriodEngagement();
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
      <el-drawer v-model="settingsVisible" :show-close="false" :size="400">
        <template #header="{ close, titleId, titleClass }">
          <h2>{{ $t('analysis.settings') }}</h2>
          <el-button type="danger" @click="close">
            <el-icon class="el-icon--left">
              <CircleCloseFilled/>
            </el-icon>
            {{ $t('general.close') }}
          </el-button>
        </template>
        <h3>{{ $t('settings.live-data-title') }}</h3>
        <h4>{{ $t('settings.live-data-refresh-interval-label') }}</h4>
        <el-input-number
            v-model="currentIntervalSeconds"
            :max="300"
            :min="3"
            @change="onCurrentIntervalSecondsChange"
        />
        <el-divider/>
        <h3>{{ $t('settings.timeline-title') }}</h3>
        <h4>{{ $t('settings.timeline-refresh-interval-label') }}</h4>
        <el-input-number
            v-model="timelineIntervalSeconds"
            :max="300"
            :min="10"
            @change="onTimelineIntervalSecondsChange"
        />
        <h4>{{ $t('settings.timeline-period-label') }}</h4>
        <el-input-number
            v-model="timelinePeriod"
            :max="120"
            :min="15"
            @change="onTimelinePeriodChange"
        />
      </el-drawer>

      <div class="info-container">
        <el-card class="info-card">
          <div class="large-text">{{ connectedUsers }}</div>
          <div>{{ $t('analysis.info-connected-users') }}</div>
        </el-card>
        <el-card class="info-card">
          <div class="large-text">{{ connectedUsers > 0 ? visibleUsers : 0 }}</div>
          <div>{{ $t('analysis.info-visible-users') }}</div>
        </el-card>
      </div>

      <el-divider/>

      <div v-if="connectedUsers > 0 && !isCurrentDataEmpty" class="visualization-container">

        <el-badge :style="{visibility: currentDataOutdated ? 'visible' : 'hidden'}"
                  :value="$t('analysis.old-data-badge')" class="old-data-badge"
                  type="warning"/>
        <MoodWave :data="currentAllData"/>

        <div class="charts-container">

          <el-card class="engagement-card">
            <template #header>
              <h2>{{ $t('analysis.engagement') }}</h2>
            </template>
            <el-badge :style="{visibility: currentDataOutdated ? 'visible' : 'hidden'}"
                      :value="$t('analysis.old-data-badge')" class="old-data-badge"
                      type="warning"/>
            <DonutChart :data="currentEngagement"/>
            <el-collapse v-model="openCollapseViews" class="collapse-view">
              <el-collapse-item name="timelineEngagement">
                <template #title>
                  <h3>{{ $t('analysis.timeline-title') }}</h3>
                </template>
                <el-badge :style="{visibility: timelineOutdated ? 'visible' : 'hidden'}"
                          :value="$t('analysis.old-data-badge')" class="old-data-badge"
                          type="warning"/>
                <LineChart v-if="timelineEngagement.length > 1" :data="timelineEngagement"/>
                <div v-else class="timeline-no-data">{{ $t('analysis.timeline-no-data') }}</div>
              </el-collapse-item>
            </el-collapse>
          </el-card>

          <div class="bar-chart-container">
            <el-card class="bar-card">
              <template #header>
                <h2>{{ $t('analysis.confusion') }}</h2>
              </template>
              <el-badge :style="{visibility: currentDataOutdated ? 'visible' : 'hidden'}"
                        :value="$t('analysis.old-data-badge')" class="old-data-badge"
                        type="warning"/>
              <BarChart
                  :data="currentConfusion"
                  :tooltipText="$t('analysis.tooltip-confused')"
                  class="bar-chart"
              />
              <el-collapse v-model="openCollapseViews" class="collapse-view">
                <el-collapse-item name="timelineConfusion">
                  <template #title>
                    <h3>{{ $t('analysis.timeline-title') }}</h3>
                  </template>
                  <el-badge :style="{visibility: timelineOutdated ? 'visible' : 'hidden'}"
                            :value="$t('analysis.old-data-badge')" class="old-data-badge"
                            type="warning"/>
                  <LineChart v-if="timelineConfusion.length > 1" :data="timelineConfusion"/>
                  <div v-else class="timeline-no-data">{{ $t('analysis.timeline-no-data') }}</div>
                </el-collapse-item>
              </el-collapse>
            </el-card>

            <el-card class="bar-card">
              <template #header>
                <h2>{{ $t('analysis.boredom') }}</h2>
              </template>
              <el-badge :style="{visibility: currentDataOutdated ? 'visible' : 'hidden'}"
                        :value="$t('analysis.old-data-badge')" class="old-data-badge"
                        type="warning"/>
              <BarChart
                  :data="currentBoredom"
                  :tooltipText="$t('analysis.tooltip-bored')"
                  class="bar-chart"
              />
              <el-collapse v-model="openCollapseViews" class="collapse-view">
                <el-collapse-item name="timelineBoredom">
                  <template #title>
                    <h3>{{ $t('analysis.timeline-title') }}</h3>
                  </template>
                  <el-badge :style="{visibility: timelineOutdated ? 'visible' : 'hidden'}"
                            :value="$t('analysis.old-data-badge')" class="old-data-badge"
                            type="warning"/>
                  <LineChart v-if="timelineBoredom.length > 1" :data="timelineBoredom"/>
                  <div v-else class="timeline-no-data">{{ $t('analysis.timeline-no-data') }}</div>
                </el-collapse-item>
              </el-collapse>
            </el-card>

            <el-card class="bar-card">
              <template #header>
                <h2>{{ $t('analysis.frustration') }}</h2>
              </template>
              <el-badge :style="{visibility: currentDataOutdated ? 'visible' : 'hidden'}"
                        :value="$t('analysis.old-data-badge')" class="old-data-badge"
                        type="warning"/>
              <BarChart
                  :data="currentFrustration"
                  :tooltipText="$t('analysis.tooltip-frustrated')"
                  class="bar-chart"
              />
              <el-collapse v-model="openCollapseViews" class="collapse-view">
                <el-collapse-item name="timelineFrustration">
                  <template #title>
                    <h3>{{ $t('analysis.timeline-title') }}</h3>
                  </template>
                  <el-badge :style="{visibility: timelineOutdated ? 'visible' : 'hidden'}"
                            :value="$t('analysis.old-data-badge')" class="old-data-badge"
                            type="warning"/>
                  <LineChart v-if="timelineFrustration.length > 1" :data="timelineFrustration"/>
                  <div v-else class="timeline-no-data">{{ $t('analysis.timeline-no-data') }}</div>
                </el-collapse-item>
              </el-collapse>
            </el-card>
          </div>

        </div>
      </div>
      <div v-else-if="connectedUsers > 0 && isCurrentDataEmpty" class="loading-data-container">
        <h2>{{ $t('analysis.connections-no-data') }}</h2>
      </div>
      <div v-else class="no-connections-container">
        <h2>{{ $t('analysis.no-connections') }}</h2>
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

.no-connections-container {
  display: flex;
  justify-content: center;
}

.loading-data-container {
  display: flex;
  justify-content: center;
}

.charts-container {
  display: flex;
  flex-wrap: wrap;
  flex-direction: row;
  justify-content: space-between;
  height: 500px;
  gap: 30px 30px;
}

.timeline-no-data {
  display: flex;
  justify-content: center;
}

.old-data-badge {
  height: 100%;
  width: 100%;
  padding-bottom: 6px;
  text-align: end;
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