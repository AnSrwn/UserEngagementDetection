import {toLocaleUtc} from "~/composables/useUtils";

export function toAvgPeriodEngagementClientItem(item: {
    from_datetime: string | number | Date;
    to_datetime: string | number | Date;
    avg_boredom: number;
    avg_engagement: number;
    avg_confusion: number;
    avg_frustration: number;
}) {
    return {
        from_datetime: item.from_datetime === null ? null : toLocaleUtc(new Date(item.from_datetime)),
        to_datetime: item.to_datetime === null ? null : toLocaleUtc(new Date(item.to_datetime)),
        avg_boredom: Number(item.avg_boredom.toFixed(2)),
        avg_engagement: Number(item.avg_engagement.toFixed(2)),
        avg_confusion: Number(item.avg_confusion.toFixed(2)),
        avg_frustration: Number(item.avg_frustration.toFixed(2)),
    };
}