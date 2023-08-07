<script setup>
import {useApiFetch} from "~/composables/useApiFetch";
import {toTimelineEngagementClientItem} from "~/composables/serverToClient";

let high = 0;
let connectedUsers = ref();
let visibleUsers = ref();
let allData = ref();
let engagementData = ref();
let boredomData = ref();
let confusionData = ref();
let frustrationData = ref();

let timelineAllData = ref([]);
let timelineEngagement = ref([]);
let timelineBoredom = ref([]);
let timelineConfusion = ref([]);
let timelineFrustration = ref([]);

let timePeriod = ref(30); // minutes

const getSimpleEngagement = async () => {
  const {data} = await useApiFetch(`engagement/average/simple`, {
    query: {interval: 5}
  });

  if (data.value !== null) {
    allData = data.value;

    connectedUsers.value = data.value.connections;
    visibleUsers.value = data.value.visible_users;

    engagementData.value = data.value.engagement;
    boredomData.value = data.value.boredom;
    confusionData.value = data.value.confusion;
    frustrationData.value = data.value.frustration;
  }
}

const getTimelinePeriodEngagement = async () => {
  let params = () => {
    let earliestFromDatetime = new Date(((new Date()).getTime() - timePeriod.value * 60000));
    let fromDatetime = earliestFromDatetime.toISOString();
    let toDatetime = (new Date()).toISOString();

    return {from_datetime: fromDatetime, to_datetime: toDatetime, interval: 5}
  }

  const {data} = await useApiFetch('engagement/average/percentage/period', {
    query: params(),
    transform: (data) => {
      return data.map((item) => toTimelineEngagementClientItem(item));
    }
  });

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

const getTimelinePointEngagement = async () => {
  const {data} = await useApiFetch(`engagement/average/percentage`, {
    query: {interval: 5},
    transform: (data) => {
      return data.map((item) => toTimelineEngagementClientItem(item));
    },
  });

  // Remove expired data
  let earliestFromDatetime = new Date(((new Date()).getTime() - timePeriod.value * 60000));
  let filtered = timelineAllData.value.filter((item) => item.from_datetime.getTime() > earliestFromDatetime.getTime())

  if (data.value !== null && data.value[0].from_datetime !== null) {
    filtered = filtered.concat(data.value);
  }

  timelineAllData.value = filtered
  timelineEngagement.value = filtered.map(item => {
    return {time: item.from_datetime, percentage: item.avg_engagement}
  });
  timelineBoredom.value = filtered.map(item => {
    return {time: item.from_datetime, percentage: item.avg_boredom}
  });
  timelineConfusion.value = filtered.map(item => {
    return {time: item.from_datetime, percentage: item.avg_confusion}
  });
  timelineFrustration.value = filtered.map(item => {
    return {time: item.from_datetime, percentage: item.avg_frustration}
  });
}

function refreshing() {
  getSimpleEngagement();
  getTimelinePointEngagement();
}

let requestInterval;

onMounted(async () => {
  await fetchOnMount(getSimpleEngagement);
  await fetchOnMount(getTimelinePeriodEngagement);
  requestInterval = setInterval(refreshing, 5000);
})

onDeactivated(() => {
  clearInterval(requestInterval);
})

onBeforeUnmount(() => {
  clearInterval(requestInterval);
})
</script>

<template>
  <div>
    <h1>{{ $t('analysis.title') }}</h1>
    <client-only>
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
      <MoodWave v-if="visibleUsers > 0" :data="allData"/>
      <div class="charts-container">
        <el-card class="engagement-card">
          <template #header>
            <h2>{{ $t('analysis.engagement') }}</h2>
          </template>
          <DonutChart v-if="visibleUsers > 0" :data="engagementData"/>
          <div v-else>{{ $t('analysis.no-data') }}</div>
          <el-divider/>
          <LineChart v-if="timelineEngagement.length > 0" :data="timelineEngagement"/>
        </el-card>
        <div class="bar-chart-container">
          <el-card class="bar-card">
            <template #header>
              <h2>{{ $t('analysis.confusion') }}</h2>
            </template>
            <BarChart
                v-if="visibleUsers > 0"
                :data="confusionData"
                :tooltipText="$t('analysis.tooltip-confused')"
                class="bar-chart"
            />
            <div v-else>{{ $t('analysis.no-data') }}</div>
            <el-divider/>
            <LineChart v-if="timelineConfusion.length > 0" :data="timelineConfusion"/>
          </el-card>
          <el-card class="bar-card">
            <template #header>
              <h2>{{ $t('analysis.boredom') }}</h2>
            </template>
            <BarChart
                v-if="visibleUsers > 0"
                :data="boredomData"
                :tooltipText="$t('analysis.tooltip-bored')"
                class="bar-chart"
            />
            <div v-else>{{ $t('analysis.no-data') }}</div>
            <el-divider/>
            <LineChart v-if="timelineBoredom.length > 0" :data="timelineBoredom"/>
          </el-card>
          <el-card class="bar-card">
            <template #header>
              <h2>{{ $t('analysis.frustration') }}</h2>
            </template>
            <BarChart
                v-if="visibleUsers > 0"
                :data="frustrationData"
                :tooltipText="$t('analysis.tooltip-frustrated')"
                class="bar-chart"
            />
            <div v-else>{{ $t('analysis.no-data') }}</div>
            <el-divider/>
            <LineChart v-if="timelineFrustration.length > 0" :data="timelineFrustration"/>
          </el-card>
        </div>
      </div>
    </client-only>
  </div>
</template>

<style lang='scss' scoped>
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
  height: 500px;
  gap: 30px 30px;
}

.engagement-card {
  max-width: 600px;
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
  max-width: 600px;
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