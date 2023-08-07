export const useApiFetch: typeof useFetch = (request, opts?) => {
    const config = useRuntimeConfig();

    return useFetch(request, { baseURL: config.public.baseUrl, ...opts })
}

export async function fetchOnMount(fetch: () => Promise<void>) {
    return await nextTick(async () => {
        await fetch();
    })
}