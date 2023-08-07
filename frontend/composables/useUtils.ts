import {Ref} from "vue";

export function toDeepRaw(array: Ref<Array<Ref<any>>>): Array<any> {
    return array.value.map(item => toRaw(item))
}