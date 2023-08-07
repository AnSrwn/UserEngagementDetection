import {Ref} from "vue";

export function toDeepRaw(array: Ref<Array<Ref<any>>>): Array<any> {
    return array.value.map(item => toRaw(item))
}

export function toLocaleUtc(isoDate: Date): Date {
    let newDate = new Date();
    newDate.setUTCFullYear(isoDate.getFullYear());
    newDate.setUTCMonth(isoDate.getMonth());
    newDate.setUTCDate(isoDate.getMonth());
    newDate.setUTCHours(isoDate.getHours());
    newDate.setUTCMinutes(isoDate.getMinutes());
    newDate.setUTCSeconds(isoDate.getSeconds());
    newDate.setUTCMilliseconds(isoDate.getMilliseconds());

    return newDate;
}